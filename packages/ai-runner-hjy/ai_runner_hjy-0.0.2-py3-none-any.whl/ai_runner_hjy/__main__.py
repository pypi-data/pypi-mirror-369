import argparse
import os
import sys


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m backend.ai_runner_hjy",
        description=(
            "Run one AI call using a config_key from RDS (OpenAI-compatible). "
            "Loads envs from project root automatically."
        ),
    )
    # legacy top-level flags (backward compatible)
    parser.add_argument(
        "-k",
        "--config-key",
        dest="config_key",
        help="ai_config.config_key to use (optional; default: first active config)",
    )
    parser.add_argument("--timeout", dest="timeout", type=int, help="override AI_TIMEOUT seconds (optional)")
    parser.add_argument("--max-retries", dest="max_retries", type=int, help="override AI_MAX_RETRIES (optional)")

    sub = parser.add_subparsers(dest="cmd")

    # legacy single config_key (explicit)
    p_once = sub.add_parser("once", help="Run once by config_key")
    p_once.add_argument("-k", "--config-key", dest="config_key")
    p_once.add_argument("--timeout", dest="timeout", type=int)
    p_once.add_argument("--max-retries", dest="max_retries", type=int)

    # route mode
    p_route = sub.add_parser("route", help="Run via project+route")
    p_route.add_argument("-p", "--project", required=True)
    p_route.add_argument("-r", "--route-key", required=True)
    p_route.add_argument("-d", "--data", help="runtime variables as JSON string", default=None)
    p_route.add_argument("--timeout", dest="timeout", type=int)
    p_route.add_argument("--max-retries", dest="max_retries", type=int)

    # dev server
    p_dev = sub.add_parser("dev", help="Run local dev sandbox server")
    p_dev.add_argument("-H", "--host", default="127.0.0.1")
    p_dev.add_argument("-P", "--port", type=int, default=5173)
    p_dev.add_argument("--enable-auth", action="store_true")

    # cfg generator
    p_cfg = sub.add_parser("cfg", help="Config generator and pooling")
    cfg_sub = p_cfg.add_subparsers(dest="cfg_cmd")
    p_cfg_gen = cfg_sub.add_parser("gen", help="Generate configs from YAML")
    p_cfg_gen.add_argument("-f", "--file", required=True, dest="cfg_file")
    p_cfg_gen.add_argument("--dry-run", action="store_true")
    p_cfg_pool = cfg_sub.add_parser("route-pool", help="Attach members to route from YAML")
    p_cfg_pool.add_argument("-f", "--file", required=True, dest="pool_file")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])

    if args.timeout is not None:
        os.environ["AI_TIMEOUT"] = str(args.timeout)
    if args.max_retries is not None:
        os.environ["AI_MAX_RETRIES"] = str(args.max_retries)

    try:
        from .core.env import load_envs, validate_envs
        load_envs()
        validate_envs()

        if args.cmd == "route":
            from .route import run_route
            import json as _json

            runtime_vars = _json.loads(args.data) if args.data else None
            if args.timeout is not None:
                os.environ["AI_TIMEOUT"] = str(args.timeout)
            if args.max_retries is not None:
                os.environ["AI_MAX_RETRIES"] = str(args.max_retries)
            status, resp = run_route(args.project, args.route_key, runtime_variables=runtime_vars)
            print(resp)
            return 0 if 200 <= status < 300 else 1
        elif args.cmd == "dev":
            if args.enable_auth:
                os.environ["ENABLE_AUTH"] = "true"
            from .dev_server import run_dev
            run_dev(args.host, args.port)
            return 0
        elif args.cmd == "cfg":
            import yaml  # type: ignore
            from .cfg_tool import (
                upsert_connection, upsert_model, upsert_param_profile,
                upsert_prompt, upsert_config, pool_members
            )
            from .core.db import get_db_connection
            if args.cfg_cmd == "gen":
                with open(args.cfg_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                project = data.get("project") or "project"
                defaults = data.get("defaults") or {}
                provider = (defaults.get("provider") or "provider").lower()
                params = (defaults.get("params") or {})
                prompts = data.get("prompts") or []
                endpoints = data.get("endpoints") or []
                features = data.get("features") or []
                if not prompts:
                    raise SystemExit("No prompts in yaml")
                prm = prompts[0]
                pr_name = prm.get("name"); pr_ver = prm.get("version")
                pr_msgs = prm.get("messages"); pr_rf = prm.get("response_format") or {}
                pr_vars = prm.get("variables") or {}

                # dry-run summary
                planned = []
                for ep in endpoints:
                    base_url = ep.get("base_url"); api_env = ep.get("api_key_env")
                    models = ep.get("models") or []
                    for model in models:
                        feat = features[0].get("feature_key") if features else "feat"
                        ck = f"{project}_{provider}_{str(model).replace('/', '_')}__{feat}"
                        planned.append(ck)
                if args.dry_run:
                    print("Planned config_keys:")
                    for ck in planned:
                        print("-", ck)
                    return 0

                with get_db_connection() as conn:
                    cur = conn.cursor()
                    # shared prompt/param_profile
                    pp_id = upsert_param_profile(cur, f"default_{pr_name}", params)
                    pr_id = upsert_prompt(cur, pr_name, pr_ver, pr_msgs, pr_rf, pr_vars)
                    for ep in endpoints:
                        base_url = ep.get("base_url"); api_env = ep.get("api_key_env")
                        api_key = os.environ.get(api_env or "") or ""
                        if not api_key:
                            raise SystemExit(f"Missing env {api_env} for endpoint API key")
                        conn_id = upsert_connection(cur, f"{provider}_{project}", provider, base_url, api_key)
                        for model in ep.get("models") or []:
                            model_id = upsert_model(cur, str(model), conn_id)
                            feat = features[0].get("feature_key") if features else "feat"
                            ck = f"{project}_{provider}_{str(model).replace('/', '_')}__{feat}"
                            upsert_config(cur, ck, model_id, pp_id, pr_id, description=f"{project}:{pr_name}:{pr_ver}")
                print("OK: configs generated")
                return 0

            elif args.cfg_cmd == "route-pool":
                with open(args.pool_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                project = data.get("project"); route_key = data.get("route_key"); policy = data.get("policy") or "primary_backup"
                members = data.get("members") or []
                from .core.db import get_db_connection
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    pool_members(cur, project, route_key, members, policy=policy)
                print("OK: route pool updated")
                return 0
            else:
                print("Missing cfg subcommand (gen / route-pool)")
                return 2
        else:
            # default legacy
            if args.timeout is not None:
                os.environ["AI_TIMEOUT"] = str(args.timeout)
            if args.max_retries is not None:
                os.environ["AI_MAX_RETRIES"] = str(args.max_retries)
            from .run import run_once
            run_once(getattr(args, "config_key", None))
            return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        # Minimal stderr reporting; detailed logs already handled inside run_once
        sys.stderr.write(f"Error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

