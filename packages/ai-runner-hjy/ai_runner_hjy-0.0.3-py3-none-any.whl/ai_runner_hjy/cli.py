# backend/ai_runner_hjy/cli.py

import argparse
import json
import os
import sys
from pprint import pprint

from .core.config import AppConfig, get_config, validate_required_fields
from .run import run_once
from .route import run_route
from .dev_server import run_dev_server
from .cfg_tool import generate_configs_from_yaml, pool_members_from_yaml
from .cfg_tool import dump_schema, generate_sample_yaml, verify_yaml
from .quickstart import run_quickstart, run_quickstart_demo
from .doctor import run_doctor

def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="AI Runner Hjy: A DB-config driven OpenAI-compatible caller.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # `run-once` command
    run_once_parser = subparsers.add_parser("run-once", help="Run a single config_key.")
    run_once_parser.add_argument("config_key", help="The config_key to run.")

    # `route` command
    route_parser = subparsers.add_parser("route", help="Run a v2 route.")
    route_parser.add_argument("-p", "--project", required=True, help="Project name.")
    route_parser.add_argument("-r", "--route", required=True, help="Route key.")
    route_parser.add_argument("-d", "--data", type=json.loads, default={}, help='JSON string of dynamic variables, e.g., \'{"key":"value"}\'')
    route_parser.add_argument("-f", "--file", help="Path to a JSON file containing dynamic variables.")

    # `dev` command
    dev_parser = subparsers.add_parser("dev", help="Run the interactive dev server (HMAC disabled).")
    dev_parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to.")
    dev_parser.add_argument("--port", type=int, default=8899, help="Port to run the server on.")

    # `init` command
    init_parser = subparsers.add_parser("init", help="Environment & DB readiness check (no side effects)")
    init_parser.add_argument("--env-only", action="store_true", help="Only check environment variables & python/deps/tmp")
    init_parser.add_argument("--db-only", action="store_true", help="Only check DB connectivity")
    init_parser.add_argument("--dev-port", type=int, default=None, help="Probe and persist a free dev server port (e.g., 8899)")

    # `cfg` command group
    cfg_parser = subparsers.add_parser("cfg", help="Configuration management tools.")
    cfg_subparsers = cfg_parser.add_subparsers(dest="cfg_command", required=True)

    # `cfg gen`
    cfg_gen_parser = cfg_subparsers.add_parser("gen", help="Generate configs from YAML.")
    cfg_gen_parser.add_argument("-f", "--file", required=True, help="Path to configs.yaml.")

    # `cfg route-pool`
    cfg_pool_parser = cfg_subparsers.add_parser("route-pool", help="Pool members to a route from YAML.")
    cfg_pool_parser.add_argument("-f", "--file", required=True, help="Path to members.yaml.")
    cfg_pool_parser.add_argument("--append", action="store_true", help="Append mode (keep existing members, don't deactivate).")
    cfg_pool_parser.add_argument("--dry-run", action="store_true", help="Perform a dry run (no changes to DB).")

    # `cfg dump-schema`
    cfg_dump_parser = cfg_subparsers.add_parser("dump-schema", help="Export DB schema (read-only) to docs/SCHEMA_AUTO.md and docs/schema_dump.json")
    cfg_dump_parser.add_argument("--db", dest="db_name", default=None, help="Target database name (default: MYSQL_AI_DATABASE)")
    cfg_dump_parser.add_argument("--prefix", dest="table_prefix", default="ai_", help="Table name prefix to include (default: ai_)")
    cfg_dump_parser.add_argument("--out", dest="out_md", default="docs/SCHEMA_AUTO.md", help="Markdown output path")
    cfg_dump_parser.add_argument("--json", dest="out_json", default="docs/schema_dump.json", help="JSON output path")

    # `cfg sample`
    cfg_sample_parser = cfg_subparsers.add_parser("sample", help="Generate a full-stack YAML template")
    cfg_sample_parser.add_argument("--provider", choices=["openrouter", "custom"], default="openrouter")
    cfg_sample_parser.add_argument("--out", dest="out_file", default="tmp/configs_full.yaml")

    # `cfg verify`
    cfg_verify_parser = cfg_subparsers.add_parser("verify", help="Validate a full-stack YAML without DB writes")
    cfg_verify_parser.add_argument("-f", "--file", dest="verify_file", required=True, help="Path to YAML file")
    cfg_verify_parser.add_argument("--db-check", action="store_true", help="Also check DB for existing config_key (read-only)")

    # quickstart
    quickstart_parser = subparsers.add_parser("quickstart", help="3-minute success path (local|rds|demo)")
    quickstart_parser.add_argument("--mode", choices=["local", "rds", "demo"], default="local")
    quickstart_parser.add_argument("--media-path", dest="media_path", default=None, help="demo mode: path to local media file")

    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Environment/DB diagnostics with human-readable remediation")
    doctor_parser.add_argument("--env-only", action="store_true", help="Only check environment variables and config validation")
    doctor_parser.add_argument("--db-only", action="store_true", help="Only check DB connectivity")
    doctor_parser.add_argument("--timeout", type=float, default=3.0, help="TCP connect timeout seconds (default: 3.0)")


    # --- Execution ---
    args = parser.parse_args()

    try:
        config = get_config()
        # Strict validation of mandatory fields
        validate_required_fields(config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    if args.command == "run-once":
        run_once(config_key=args.config_key, config=config)
    elif args.command == "route":
        variables = args.data
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    variables.update(json.load(f))
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading variables file {args.file}: {e}", file=sys.stderr)
                sys.exit(1)

        result = run_route(
            project=args.project, 
            route_key=args.route, 
            runtime_variables=variables,
            config=config
        )
        pprint(result)
    elif args.command == "dev":
        run_dev_server(config=config, host=args.host, port=args.port)
    elif args.command == "cfg":
        if args.cfg_command == "gen":
            generate_configs_from_yaml(args.file, config)
        elif args.cfg_command == "route-pool":
            pool_members_from_yaml(args.file, config, exclusive=not args.append, dry_run=args.dry_run)
        elif args.cfg_command == "dump-schema":
            try:
                dump_schema(db_name=args.db_name, table_prefix=args.table_prefix, out_md=args.out_md, out_json=args.out_json, config=config)
                print(f"Schema exported to {args.out_md} and {args.out_json}")
            except Exception as e:
                print(f"Schema export failed: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.cfg_command == "sample":
            try:
                generate_sample_yaml(args.provider, args.out_file)
                print(f"Sample YAML generated at {args.out_file}")
            except Exception as e:
                print(f"Sample generation failed: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.cfg_command == "verify":
            try:
                issues = verify_yaml(args.verify_file, config, db_check=args.db_check)
                if issues:
                    sys.exit(1)
            except Exception as e:
                print(f"Verify failed: {e}", file=sys.stderr)
                sys.exit(1)
    elif args.command == "init":
        from .init_check import run_init
        code = run_init(config=config, env_only=args.env_only, db_only=args.db_only, dev_port=args.dev_port)
        sys.exit(code)
    elif args.command == "quickstart":
        if args.mode == "demo":
            code = run_quickstart_demo(media_path=args.media_path)
        else:
            code = run_quickstart(mode=args.mode)
        sys.exit(code)
    elif args.command == "doctor":
        code = run_doctor(env_only=args.env_only, db_only=args.db_only, timeout_sec=args.timeout)
        sys.exit(code)

if __name__ == "__main__":
    main()