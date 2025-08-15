from __future__ import annotations

"""Config generator (v0.0.2 feature)

CLI entrypoints (to be wired later):
  - cfg gen -f configs.yaml  (dry-run optional)
  - route pool -p <project> -r <route> -f members.yaml

API functions exposed for tests/scripts.
"""

import os
import json
from typing import Any, Dict, List, Tuple
from datetime import datetime

import yaml
from dotenv import load_dotenv

from .core.config import AppConfig
from .core.db import get_db_connection
from .core.crypto_utils import encrypt_api_key
from .core.crud import (
    upsert_connection,
    upsert_model,
    upsert_param_profile,
    upsert_prompt,
    upsert_config,
)


def upsert_connection(cur, name: str, provider: str, base_url: str, api_key_plain: str, config: AppConfig) -> int:
    blob = encrypt_api_key(api_key_plain, config.ai_pepper)
    cur.execute(
        "SELECT id FROM ai_connection WHERE name=%s LIMIT 1", (name,)
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE ai_connection SET provider=%s, base_url=%s, api_key_encrypted=%s, is_active=1 WHERE id=%s",
            (provider, base_url, json.dumps(blob, ensure_ascii=False), int(row[0])),
        )
        return int(row[0])
    cur.execute(
        "INSERT INTO ai_connection(name,provider,base_url,api_key_encrypted,is_active) VALUES(%s,%s,%s,%s,1)",
        (name, provider, base_url, json.dumps(blob, ensure_ascii=False)),
    )
    return int(cur.lastrowid)


def upsert_model(cur, name: str, connection_id: int) -> int:
    cur.execute("SELECT id FROM ai_model WHERE name=%s LIMIT 1", (name,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE ai_model SET connection_id=%s, is_active=1 WHERE id=%s", (connection_id, int(row[0])))
        return int(row[0])
    cur.execute(
        "INSERT INTO ai_model(name,connection_id,is_active) VALUES(%s,%s,1)", (name, connection_id)
    )
    return int(cur.lastrowid)


def upsert_param_profile(cur, name: str, params: Dict[str, Any]) -> int:
    cur.execute("SELECT id FROM ai_param_profile WHERE name=%s LIMIT 1", (name,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE ai_param_profile SET params_json=%s, is_active=1 WHERE id=%s", (json.dumps(params, ensure_ascii=False), int(row[0])))
        return int(row[0])
    cur.execute(
        "INSERT INTO ai_param_profile(name,params_json,is_active) VALUES(%s,%s,1)", (name, json.dumps(params, ensure_ascii=False))
    )
    return int(cur.lastrowid)


def upsert_prompt(cur, name: str, version: str, messages: Any, response_format: Dict[str, Any], variables: Dict[str, Any]) -> int:
    cur.execute("SELECT id FROM ai_prompt WHERE name=%s AND version=%s LIMIT 1", (name, version))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE ai_prompt SET messages_json=%s, response_format_json=%s, variables_json=%s, status='active' WHERE id=%s",
            (json.dumps(messages, ensure_ascii=False), json.dumps(response_format, ensure_ascii=False), json.dumps(variables, ensure_ascii=False), int(row[0]))
        )
        return int(row[0])
    cur.execute(
        "INSERT INTO ai_prompt(name,version,description,messages_json,response_format_json,variables_json,status) VALUES(%s,%s,%s,%s,%s,%s,'active')",
        (name, version, f"{name} {version}", json.dumps(messages, ensure_ascii=False), json.dumps(response_format, ensure_ascii=False), json.dumps(variables, ensure_ascii=False))
    )
    return int(cur.lastrowid)


def upsert_config(cur, config_key: str, model_id: int, param_profile_id: int, prompt_id: int, description: str = "") -> int:
    cur.execute("SELECT id FROM ai_config WHERE config_key=%s LIMIT 1", (config_key,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE ai_config SET model_id=%s, param_profile_id=%s, prompt_id=%s, description=%s, is_active=1 WHERE id=%s",
            (model_id, param_profile_id, prompt_id, description, int(row[0]))
        )
        return int(row[0])
    cur.execute(
        "INSERT INTO ai_config(config_key,model_id,param_profile_id,prompt_id,description,is_active) VALUES(%s,%s,%s,%s,%s,1)",
        (config_key, model_id, param_profile_id, prompt_id, description)
    )
    return int(cur.lastrowid)


def pool_members(cur, project: str, route_key: str, members: List[Dict[str, Any]], policy: str = "primary_backup", exclusive: bool = True, dry_run: bool = False) -> List[str]:
    # ensure project/route
    cur.execute("INSERT INTO ai_project_v2(name,status) VALUES(%s,'active') ON DUPLICATE KEY UPDATE status='active'", (project,))
    cur.execute("SELECT id FROM ai_project_v2 WHERE name=%s LIMIT 1", (project,))
    pid = int(cur.fetchone()[0])

    cur.execute(
        "INSERT INTO ai_route_v2(project_id,route_key,policy,is_active) VALUES(%s,%s,%s,1) ON DUPLICATE KEY UPDATE policy=VALUES(policy), is_active=1",
        (pid, route_key, policy)
    )
    cur.execute("SELECT id FROM ai_route_v2 WHERE project_id=%s AND route_key=%s LIMIT 1", (pid, route_key))
    rid = int(cur.fetchone()[0])

    changes = []
    # Get existing members for exclusive mode
    existing_members = []
    if exclusive:
        cur.execute("SELECT config_id FROM ai_route_member_v2 WHERE route_id=%s AND is_active=1", (rid,))
        existing_members = [row[0] for row in cur.fetchall()]

    # Process YAML members
    yaml_config_ids = set()
    for m in members:
        cfg_key = m["config_key"]; prio = int(m.get("priority", 1));
        cur.execute("SELECT id FROM ai_config WHERE config_key=%s LIMIT 1", (cfg_key,))
        cfg_row = cur.fetchone()
        if not cfg_row:
            raise RuntimeError(f"config_key not found: {cfg_key}")
        cfg_id = int(cfg_row[0])
        yaml_config_ids.add(cfg_id)

        if dry_run:
            cur.execute("SELECT id FROM ai_route_member_v2 WHERE route_id=%s AND config_id=%s LIMIT 1", (rid, cfg_id))
            existing = cur.fetchone()
            if existing:
                changes.append(f"update member: {cfg_key} (priority={prio})")
            else:
                changes.append(f"add member: {cfg_key} (priority={prio})")
            continue

        cur.execute("SELECT id FROM ai_route_member_v2 WHERE route_id=%s AND config_id=%s LIMIT 1", (rid, cfg_id))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE ai_route_member_v2 SET is_active=1, priority=%s WHERE id=%s", (prio, int(row[0])))
            changes.append(f"updated member: {cfg_key} (priority={prio})")
        else:
            cur.execute("INSERT INTO ai_route_member_v2(route_id,config_id,priority,is_active) VALUES(%s,%s,%s,1)", (rid, cfg_id, prio))
            changes.append(f"added member: {cfg_key} (priority={prio})")

    # Handle exclusive mode: deactivate members not in YAML
    if exclusive and not dry_run:
        to_deactivate = set(existing_members) - yaml_config_ids
        if to_deactivate:
            # Handle single item case
            if len(to_deactivate) == 1:
                config_id = list(to_deactivate)[0]
                cur.execute("UPDATE ai_route_member_v2 SET is_active=0 WHERE route_id=%s AND config_id=%s", (rid, config_id))
            else:
                placeholders = ','.join(['%s'] * len(to_deactivate))
                cur.execute(f"UPDATE ai_route_member_v2 SET is_active=0 WHERE route_id=%s AND config_id IN ({placeholders})", (rid,) + tuple(to_deactivate))
            changes.append(f"deactivated {len(to_deactivate)} members not in YAML")
    elif exclusive and dry_run:
        to_deactivate = set(existing_members) - yaml_config_ids
        if to_deactivate:
            changes.append(f"would deactivate {len(to_deactivate)} members not in YAML")

    return changes


def dry_run_summary(changes: List[str]) -> str:
    return "\n".join(f"- {c}" for c in changes)


def generate_configs_from_yaml(file_path: str, config: AppConfig):
    """Parses a YAML file and upserts entries.

    Backward compatible behavior:
      - legacy schema: configs[{config_key, model_id, param_profile_id, prompt_id, ...}]
      - fullstack schema: connections/models/param_profiles/prompts/configs by names
        (delegates to config_ops.fullstack_gen)
    """
    import yaml
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Detect fullstack schema
    if any(k in data for k in ("connections", "models", "param_profiles", "prompts")):
        from .config_ops.fullstack_gen import generate_fullstack_from_yaml_dict
        try:
            changes = generate_fullstack_from_yaml_dict(data, config)
            print("Fullstack YAML generation completed.")
            print(dry_run_summary(changes))
            return
        except Exception as e:
            print(f"Fullstack generation failed: {e}")
            raise

    # legacy schema path
    configs_to_gen = data.get("configs", [])
    if not configs_to_gen:
        print("No 'configs' found in YAML file. Nothing to do.")
        return

    changes = []
    with get_db_connection(config) as conn:
        with conn.cursor() as cur:
            for config_data in configs_to_gen:
                config_key = config_data.get("config_key")
                model_id = config_data.get("model_id")
                param_profile_id = config_data.get("param_profile_id")
                prompt_id = config_data.get("prompt_id")
                description = config_data.get("description", "")

                if not all([config_key, model_id, param_profile_id, prompt_id]):
                    print(f"Skipping invalid config entry: {config_data}")
                    continue

                upsert_config(cur, config_key, model_id, param_profile_id, prompt_id, description)
                changes.append(f"Upserted config: {config_key}")
        conn.commit()

    print("YAML config generation completed.")
    print(dry_run_summary(changes))

def pool_members_from_yaml(file_path: str, config: AppConfig, exclusive: bool = True, dry_run: bool = False):
    """Parses a YAML file and pools members to a route."""
    import yaml
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    project = data.get("project_name")
    route_key = data.get("route_key")
    policy = data.get("policy", "primary_backup")
    members = data.get("members", [])

    if not all([project, route_key, members]):
        print("YAML file must contain project_name, route_key, and members. Nothing to do.")
        return
        
    with get_db_connection(config) as conn:
        with conn.cursor() as cur:
            changes = pool_members(cur, project, route_key, members, policy, exclusive, dry_run)
        conn.commit()
    
    if dry_run:
        print(f"Dry run for route '{project}/{route_key}':")
        for change in changes:
            print(f"  - {change}")
    else:
        print(f"Successfully updated route '{project}/{route_key}':")
        for change in changes:
            print(f"  - {change}")


def dump_schema(*, db_name: str | None, table_prefix: str, out_md: str, out_json: str, config: AppConfig) -> None:
    """
    Read-only export of table DDLs and column metadata to Markdown and JSON files.

    - Enumerates tables in the target DB (default to config.mysql_ai_database)
    - Filters by table_prefix (e.g., "ai_")
    - For each table, collects SHOW CREATE TABLE and SHOW FULL COLUMNS
    - Writes docs/SCHEMA_AUTO.md and docs/schema_dump.json (paths configurable)
    """
    target_db = db_name or config.mysql_ai_database
    if not target_db:
        raise ValueError("No database specified. Provide --db or set MYSQL_AI_DATABASE")

    # Ensure parent dirs exist
    for path in (out_md, out_json):
        import os
        d = os.path.dirname(path)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

    exported_at = datetime.utcnow().isoformat() + "Z"
    result: Dict[str, Any] = {"database": target_db, "exportedAt": exported_at, "prefix": table_prefix, "tables": []}

    with get_db_connection(config, db_name=target_db) as conn:
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        table_rows = cur.fetchall() or []
        table_names = [row[0] for row in table_rows if row and isinstance(row[0], str)]
        table_names = [t for t in table_names if t.startswith(table_prefix)] if table_prefix else table_names

        for tbl in table_names:
            # SHOW CREATE TABLE
            cur.execute(f"SHOW CREATE TABLE `{tbl}`")
            create_row = cur.fetchone()
            create_sql = None
            if create_row and len(create_row) >= 2:
                create_sql = create_row[1]

            # SHOW FULL COLUMNS
            cur.execute(f"SHOW FULL COLUMNS FROM `{tbl}`")
            columns = cur.fetchall() or []
            # Column headers vary by driver; fetch description
            col_headers = [d[0] for d in cur.description] if getattr(cur, "description", None) else []
            cols_as_dicts: List[Dict[str, Any]] = []
            for row in columns:
                try:
                    # row may be tuple; map by headers when available
                    if col_headers and isinstance(row, (list, tuple)):
                        cols_as_dicts.append({col_headers[i]: row[i] for i in range(min(len(col_headers), len(row)))})
                    else:
                        cols_as_dicts.append({"raw": row})
                except Exception:
                    cols_as_dicts.append({"raw": row})

            result["tables"].append({
                "name": tbl,
                "createTable": create_sql,
                "columns": cols_as_dicts,
            })

    # Write JSON
    import json as _json
    with open(out_json, "w", encoding="utf-8") as jf:
        _json.dump(result, jf, ensure_ascii=False, indent=2)

    # Write Markdown
    lines: List[str] = []
    lines.append(f"# RDS Schema Export\n")
    lines.append(f"- Database: `{target_db}`\n")
    lines.append(f"- Prefix: `{table_prefix}`\n")
    lines.append(f"- Exported At (UTC): `{exported_at}`\n")
    lines.append("")
    for t in result["tables"]:
        lines.append(f"## `{t['name']}`\n")
        if t.get("createTable"):
            lines.append("```sql")
            lines.append(t["createTable"])
            lines.append("```")
        if t.get("columns"):
            lines.append("")
            lines.append("<details><summary>Columns</summary>")
            lines.append("")
            # Render minimal columns table when possible
            # Try common fields: Field, Type, Null, Key, Default, Extra, Comment
            try:
                # Detect fields
                header_candidates = ["Field", "Type", "Null", "Key", "Default", "Extra", "Comment"]
                headers = [h for h in header_candidates if any(h in c for c in t["columns"][0].keys())] if t["columns"] and isinstance(t["columns"][0], dict) else []
                if headers:
                    lines.append("| " + " | ".join(headers) + " |")
                    lines.append("|" + "|".join([" --- "] * len(headers)) + "|")
                    for c in t["columns"]:
                        row = [str(c.get(h, "")) for h in headers]
                        lines.append("| " + " | ".join(row) + " |")
                else:
                    # Fallback raw dump
                    lines.append("```json")
                    lines.append(_json.dumps(t["columns"], ensure_ascii=False, indent=2))
                    lines.append("```")
            except Exception:
                lines.append("```json")
                lines.append(_json.dumps(t["columns"], ensure_ascii=False, indent=2))
                lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    with open(out_md, "w", encoding="utf-8") as mf:
        mf.write("\n".join(lines))


def generate_sample_yaml(provider: str, out_file: str) -> None:
    """
    Generate a full-stack YAML template with sections: connections/models/param_profiles/prompts/configs.
    Provider presets: openrouter | custom
    """
    import os
    os.makedirs(os.path.dirname(out_file) or ".", exist_ok=True)

    if provider == "openrouter":
        base_url = "https://openrouter.ai/api/v1/chat/completions"
        prov = "openrouter"
        model_name = "gemini-2.5-flash"
    else:
        base_url = "https://api.example.com/v1/chat/completions"
        prov = "custom"
        model_name = "demo-model"

    content = f"""# Full-stack config template (provider: {provider})
# Fill the placeholders and run:
#   ai-runner cfg gen -f <this-file>

connections:
  - name: {prov}_default
    provider: {prov}
    base_url: {base_url}
    # Plain API key will be encrypted with AI_PEPPER and persisted as JSON blob
    api_key_plain: YOUR_API_KEY

models:
  - name: {model_name}
    connection: {prov}_default

param_profiles:
  - name: default_json
    params:
      TEMPERATURE: 0.2
      MAX_TOKENS: 256
      JSON_SCHEMA_ENFORCE: true

prompts:
  - name: single_chat_zh
    version: v1
    messages:
      - role: system
        content: "只输出 JSON，不要多余文本"
      - role: user
        content: "问题：{{QUESTION}}"
    response_format:
      type: json_object
    variables:
      QUESTION: "给我一句鼓励的话"

configs:
  - config_key: {model_name.replace('-', '')}_single_chat
    model: {model_name}
    param_profile: default_json
    prompt:
      name: single_chat_zh
      version: v1
    description: "单轮中文对话 JSON 输出"
"""

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)


def verify_yaml(file_path: str, config: AppConfig, db_check: bool = False) -> int:
    """
    Verify a full-stack YAML before importing. Returns number of issues found.
    Checks:
      - Required sections/fields present
      - References (model->connection, config->model/param_profile/prompt)
      - Optional DB checks when db_check=True (e.g., config_key existence)
    """
    import yaml
    issues: List[str] = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"YAML load failed: {e}")
        return 1

    conns = {c.get('name'): c for c in (data.get('connections') or [])}
    models = {m.get('name'): m for m in (data.get('models') or [])}
    pps = {p.get('name'): p for p in (data.get('param_profiles') or [])}
    prompts = {(p.get('name'), p.get('version')): p for p in (data.get('prompts') or [])}
    configs = data.get('configs') or []

    # Basic presence
    if not conns:
        issues.append("connections: missing or empty")
    if not models:
        issues.append("models: missing or empty")
    if not pps:
        issues.append("param_profiles: missing or empty")
    if not prompts:
        issues.append("prompts: missing or empty")
    if not configs:
        issues.append("configs: missing or empty")

    # Field checks
    for name, c in conns.items():
        for fld in ("name", "provider", "base_url"):
            if not c.get(fld):
                issues.append(f"connection '{name}': missing field '{fld}'")

    for name, m in models.items():
        if not m.get('connection'):
            issues.append(f"model '{name}': missing 'connection'")
        elif m['connection'] not in conns:
            issues.append(f"model '{name}': connection '{m['connection']}' not defined")

    for name, pp in pps.items():
        if not isinstance(pp.get('params'), dict):
            issues.append(f"param_profile '{name}': 'params' must be a mapping")

    for (pname, ver), pr in prompts.items():
        if not pr.get('messages'):
            issues.append(f"prompt '{pname}/{ver}': missing 'messages'")

    seen_cfg_keys: set[str] = set()
    for cfg in configs:
        ck = cfg.get('config_key')
        if not ck:
            issues.append("config: missing 'config_key'")
            continue
        if ck in seen_cfg_keys:
            issues.append(f"config_key duplicated in YAML: {ck}")
        seen_cfg_keys.add(ck)

        mname = cfg.get('model')
        if not mname or mname not in models:
            issues.append(f"config '{ck}': model '{mname}' not defined")

        ppname = cfg.get('param_profile')
        if not ppname or ppname not in pps:
            issues.append(f"config '{ck}': param_profile '{ppname}' not defined")

        p = cfg.get('prompt') or {}
        key = (p.get('name'), p.get('version'))
        if key not in prompts:
            issues.append(f"config '{ck}': prompt '{key[0]}/{key[1]}' not defined")

    # Optional DB check: does config_key already exist?
    if db_check and seen_cfg_keys:
        try:
            with get_db_connection(config) as conn:
                cur = conn.cursor()
                for ck in seen_cfg_keys:
                    cur.execute("SELECT id FROM ai_config WHERE config_key=%s LIMIT 1", (ck,))
                    row = cur.fetchone()
                    if row:
                        issues.append(f"db: config_key already exists: {ck}")
        except Exception as e:
            issues.append(f"db check failed: {e}")

    if issues:
        print("Verify FAILED. Issues:")
        for i in issues:
            print(f" - {i}")
        print(f"Total issues: {len(issues)}")
        return len(issues)

    print("Verify PASSED. No issues found.")
    return 0

if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="AI Runner Hjy Configuration Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # `gen` command
    gen_parser = subparsers.add_parser(
        "gen", help="Generate ai_config entries from a YAML file."
    )
    gen_parser.add_argument(
        "-f", "--file", required=True, help="Path to the configs YAML file."
    )

    # `cfg route-pool`
    pool_parser = subparsers.add_parser(
        "route-pool", help="Pool config members to a route from a YAML file."
    )
    pool_parser.add_argument(
        "-f", "--file", required=True, help="Path to the members YAML file."
    )
    pool_parser.add_argument(
        "--append", action="store_true", help="Append mode (keep existing members, don't deactivate)."
    )
    pool_parser.add_argument(
        "--dry-run", action="store_true", help="Perform a dry run (no changes to DB)."
    )

    args = parser.parse_args()

    # Setup environment
    from .core.config import get_config
    try:
        config = get_config()
        print("--- Environment variables loaded and validated ---")
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    if args.command == "gen":
        print(f"--- Generating configs from {args.file} ---")
        generate_configs_from_yaml(args.file, config)
    elif args.command == "route-pool":
        print(f"--- Pooling members from {args.file} ---")
        pool_members_from_yaml(args.file, config, exclusive=not args.append, dry_run=args.dry_run)

