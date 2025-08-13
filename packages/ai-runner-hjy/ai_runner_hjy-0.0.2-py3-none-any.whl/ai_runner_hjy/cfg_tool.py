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

from backend.ai_runner_hjy.core.db import get_db_connection
from backend.ai_runner_hjy.core.crypto_utils import encrypt_api_key


def upsert_connection(cur, name: str, provider: str, base_url: str, api_key_plain: str) -> int:
    blob = encrypt_api_key(api_key_plain, os.environ.get("AI_PEPPER", ""))
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


def generate_configs_from_yaml(file_path: str):
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
        from backend.ai_runner_hjy.config_ops.fullstack_gen import generate_fullstack_from_yaml_dict
        try:
            changes = generate_fullstack_from_yaml_dict(data)
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
    with get_db_connection() as conn:
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

def pool_members_from_yaml(file_path: str, exclusive: bool = True, dry_run: bool = False):
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
        
    with get_db_connection() as conn:
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


if __name__ == "__main__":
    import argparse

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
    from backend.ai_runner_hjy.core.env import load_envs, validate_envs
    print("--- Loading environment variables ---")
    load_envs()
    validate_envs()
    print("--- Environment variables loaded and validated ---\n")
    
    if args.command == "gen":
        print(f"--- Generating configs from {args.file} ---")
        generate_configs_from_yaml(args.file)
    elif args.command == "route-pool":
        print(f"--- Pooling members from {args.file} ---")
        pool_members_from_yaml(args.file, exclusive=not args.append, dry_run=args.dry_run)

