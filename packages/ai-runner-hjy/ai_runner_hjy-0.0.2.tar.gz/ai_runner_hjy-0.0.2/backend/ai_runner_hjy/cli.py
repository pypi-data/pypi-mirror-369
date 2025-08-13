# backend/ai_runner_hjy/cli.py

import argparse
import json
import os
import sys
from pprint import pprint

from backend.ai_runner_hjy.core.env import load_envs, validate_envs
from backend.ai_runner_hjy.run import run_once
from backend.ai_runner_hjy.route import run_route
from backend.ai_runner_hjy.dev_server import run_dev_server
from backend.ai_runner_hjy.cfg_tool import generate_configs_from_yaml, pool_members_from_yaml

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


    # --- Execution ---
    args = parser.parse_args()

    load_envs()
    validate_envs()

    if args.command == "run-once":
        run_once(args.config_key)
    elif args.command == "route":
        variables = args.data
        if args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    variables.update(json.load(f))
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error reading variables file {args.file}: {e}", file=sys.stderr)
                sys.exit(1)

        result = run_route(project=args.project, route_key=args.route, runtime_variables=variables)
        pprint(result)
    elif args.command == "dev":
        run_dev_server(host=args.host, port=args.port)
    elif args.command == "cfg":
        if args.cfg_command == "gen":
            generate_configs_from_yaml(args.file)
        elif args.cfg_command == "route-pool":
            pool_members_from_yaml(args.file, exclusive=not args.append, dry_run=args.dry_run)
    elif args.command == "init":
        from backend.ai_runner_hjy.init_check import run_init
        code = run_init(env_only=args.env_only, db_only=args.db_only, dev_port=args.dev_port)
        sys.exit(code)

if __name__ == "__main__":
    main()