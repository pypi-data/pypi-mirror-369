import os
import subprocess
from typing import Optional

from .core.config import AppConfig, get_config, validate_required_fields
from .core.db import get_db_connection
from .run import run_once
from .cfg_tool import dump_schema
from .cfg_tool import generate_configs_from_yaml, pool_members_from_yaml
from .core.oss import get_oss_bucket, _generate_upload_object_name
from .core.redact import redact_url, demo_response_shape


def _which(cmd: str) -> bool:
    from shutil import which as _which
    return _which(cmd) is not None


def _write_mysql_env_if_absent(target_path: str = "mysql.env") -> None:
    if os.path.exists(target_path):
        return
    content = (
        "MYSQL_HOST=127.0.0.1\n"
        "MYSQL_PORT=3307\n"
        "MYSQL_USER=ai\n"
        "MYSQL_PASSWORD=ai123\n"
        "MYSQL_AI_DATABASE=ai_config\n"
        "AI_PEPPER=dev_only_pepper\n"
    )
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)


def run_quickstart(mode: Optional[str] = None) -> int:
    """
    Quickstart path focusing on 3-minute success.

    Modes:
      - local: spin up local MySQL (docker compose), write mysql.env, run demo
      - rds: validate env, try DB connectivity, export schema tip
    """
    if mode not in {"local", "rds", None}:
        print("Unknown mode. Use --mode local|rds", flush=True)
        return 2

    if mode in (None, "local"):
        # Prefer local path by default for instant success
        if not _which("docker"):
            print("Docker not found. Please install Docker Desktop.", flush=True)
            return 1
        # Docker Compose v2 is `docker compose`
        try:
            subprocess.run(["docker", "compose", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            print("Docker Compose not available. Please ensure 'docker compose' works.", flush=True)
            return 1

        # Ensure compose file exists in cwd
        compose_path = os.path.join(os.getcwd(), "docker-compose.yml")
        if not os.path.exists(compose_path):
            print("docker-compose.yml not found in current directory.", flush=True)
            return 1

        print("Bringing up local MySQL (port 3307)...", flush=True)
        try:
            subprocess.run(["docker", "compose", "up", "-d"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to start docker compose: {e}", flush=True)
            return 1

        _write_mysql_env_if_absent("mysql.env")
        # Load env into process for get_config()
        for line in open("mysql.env", "r", encoding="utf-8").read().splitlines():
            if not line or line.strip().startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

        # Try one run
        try:
            cfg = get_config()
            validate_required_fields(cfg)
        except Exception as e:
            print(f"Environment invalid: {e}", flush=True)
            return 1

        try:
            print("Attempting a demo run (config_key=gemini25_single_chat)...", flush=True)
            run_once(config_key="gemini25_single_chat", config=cfg)
            print("Demo run finished. Check logs table if configured.", flush=True)
        except Exception as e:
            print(f"Demo run failed: {e}", flush=True)
            return 1

        print("Quickstart (local) complete.", flush=True)
        print("Next steps: ai-runner cfg sample -> verify -> gen | ai-runner run-once <your_config_key>", flush=True)
        return 0

    # RDS path: validate env, try DB connectivity, and offer schema export
    try:
        cfg = get_config()
        validate_required_fields(cfg)
    except Exception as e:
        print(f"Environment invalid: {e}", flush=True)
        return 1

    try:
        with get_db_connection(cfg) as _:
            pass
        print("RDS connectivity OK.", flush=True)
    except Exception as e:
        print(f"RDS connectivity failed: {e}", flush=True)
        return 1

    try:
        out_md = os.path.join("docs", "SCHEMA_AUTO.md")
        out_json = os.path.join("docs", "schema_dump.json")
        os.makedirs("docs", exist_ok=True)
        dump_schema(db_name=None, table_prefix="ai_", out_md=out_md, out_json=out_json, config=cfg)
        print(f"Exported schema to {out_md} and {out_json}", flush=True)
    except Exception as e:
        print(f"Schema export skipped: {e}", flush=True)

    print("Quickstart (RDS) ready.", flush=True)
    print("Next steps: ai-runner cfg sample --out tmp/configs_full.yaml -> verify -> gen -> run-once <key>", flush=True)
    return 0


def run_quickstart_demo(media_path: Optional[str] = None) -> int:
    """Demo path: generate demo YAML -> write RDS -> upload OSS -> route call with redacted output."""
    cwd = os.getcwd()
    tmp_dir = os.path.join(cwd, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    cfg = get_config()
    try:
        validate_required_fields(cfg)
    except Exception as e:
        print(f"Environment invalid: {e}")
        return 1

    configs_path = os.path.join(tmp_dir, "configs_demo.yaml")
    members_path = os.path.join(tmp_dir, "members_demo.yaml")
    media_default = os.path.join(tmp_dir, "demo", "2.mp3")
    media_use = media_path or media_default

    os.makedirs(os.path.dirname(media_use), exist_ok=True)

    # Discover existing ids to avoid schema mismatch
    try:
        from .core.db import get_db_connection
        with get_db_connection(cfg) as conn:
            cur = conn.cursor()
            # models: pick two (no assumptions on schema columns)
            cur.execute("SELECT id FROM ai_model ORDER BY id ASC LIMIT 2")
            model_rows = cur.fetchall() or []
            model_ids = [int(r[0]) for r in model_rows]

            # param profile: pick first
            cur.execute("SELECT id FROM ai_param_profile ORDER BY id ASC LIMIT 1")
            row = cur.fetchone()
            if not row:
                print("No ai_param_profile rows found. Please create at least one.")
                return 1
            param_id = int(row[0])

            # prompt: prefer one with MEDIA_URL variable
            cur.execute("SELECT id, variables_json FROM ai_prompt ORDER BY id ASC")
            prompt_id = None
            for pid, vars_json in cur.fetchall() or []:
                try:
                    if vars_json and "MEDIA_URL" in str(vars_json):
                        prompt_id = int(pid)
                        break
                except Exception:
                    pass
            if not prompt_id:
                cur.execute("SELECT id FROM ai_prompt ORDER BY id ASC LIMIT 1")
                row = cur.fetchone()
                if not row:
                    print("No ai_prompt rows found. Please create at least one.")
                    return 1
                prompt_id = int(row[0])
    except Exception as e:
        print(f"DB discovery failed: {e}")
        return 1

    # Legacy configs YAML using discovered ids
    legacy_configs = f"""configs:\n  - config_key: demo_route_key_m1\n    model_id: {model_ids[0]}\n    param_profile_id: {param_id}\n    prompt_id: {prompt_id}\n    description: \"demo::route_key -> model1\"\n  - config_key: demo_route_key_m2\n    model_id: {model_ids[1] if len(model_ids)>1 else model_ids[0]}\n    param_profile_id: {param_id}\n    prompt_id: {prompt_id}\n    description: \"demo::route_key -> model2\"\n"""
    with open(configs_path, "w", encoding="utf-8") as f:
        f.write(legacy_configs)

    demo_members = """project_name: demo_project\nroute_key: demo_route\npolicy: primary_backup\nmembers:\n  - config_key: demo_route_key_m1\n    priority: 1\n  - config_key: demo_route_key_m2\n    priority: 2\n"""
    with open(members_path, "w", encoding="utf-8") as f:
        f.write(demo_members)

    # Write to RDS (legacy path + route members)
    try:
        generate_configs_from_yaml(configs_path, cfg)
        pool_members_from_yaml(members_path, cfg, exclusive=True, dry_run=False)
    except Exception as e:
        print(f"Writing demo YAML to RDS failed: {e}")
        return 1

    # Ensure media exists
    if not os.path.exists(media_use):
        try:
            with open(media_use, "wb") as f:
                f.write(os.urandom(1024))
        except Exception as e:
            print(f"Failed to prepare demo media file: {e}")
            return 1

    # Upload to OSS (public-read) without DB logging dependency
    bucket = get_oss_bucket(config=cfg)
    if not bucket:
        print("OSS bucket not available. Ensure OSS_ACCESS_KEY_ID/SECRET/BUCKET/ENDPOINT are set.")
        return 1
    obj = _generate_upload_object_name(cfg.project_name or "demo_project", os.path.basename(media_use))
    with open(media_use, "rb") as f:
        data = f.read()
    try:
        res = bucket.put_object(obj, data, headers={"x-oss-object-acl": "public-read"})
        if getattr(res, "status", 0) != 200:
            print(f"OSS upload failed with status {getattr(res, 'status', None)}")
            return 1
    except Exception as e:
        print(f"OSS upload error: {e}")
        return 1

    endpoint = (cfg.oss_endpoint or "").replace("https://", "").replace("http://", "")
    media_url = f"https://{cfg.oss_bucket_name}.{endpoint}/{obj}"

    # Route call
    from .route import run_route
    status, resp = run_route("demo_project", "demo_route", cfg, runtime_variables={"MEDIA_URL": media_url})

    # Redacted output + persist demo_result.json
    summary = {
        "project": "demo_project",
        "route": "demo_route",
        "policy": "primary_backup",
        "members": ["demo_route_key_m1", "demo_route_key_m2"],
        "media_url": redact_url(media_url),
        "status": status,
        "response": demo_response_shape(resp or {}),
        "note": "This is a demo. Content is for structure only; replace with your own provider/base_url/api_key.",
    }
    import json as _json
    out_json_path = os.path.join(tmp_dir, "demo_result.json")
    try:
        with open(out_json_path, "w", encoding="utf-8") as jf:
            jf.write(_json.dumps(summary, ensure_ascii=False, indent=2))
    except Exception:
        pass

    print("=== Demo Summary ===")
    print(f"project=demo_project route=demo_route policy=primary_backup")
    print(f"members=[demo_route_key_m1, demo_route_key_m2]")
    print(f"media_url={summary['media_url']}")
    print("--- Response (redacted, structure only) ---")
    print({"status": summary["status"], "response": summary["response"]})
    print(f"Saved: {out_json_path}")
    print("Tip: This is a demo. Content is for structure only; replace with your own provider/base_url/api_key.")
    return 0


