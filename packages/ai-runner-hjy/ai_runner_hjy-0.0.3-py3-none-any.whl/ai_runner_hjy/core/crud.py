from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

import mysql.connector

from .db import get_db_connection


ErrorTuple = Tuple[str, str]


def _validation_error(message: str) -> ErrorTuple:
    return ("VALIDATION_ERROR", message)


def _db_error(ex: Exception) -> ErrorTuple:
    return ("DB_ERROR", str(ex))


def add_param_profile_if_absent(
    name: str, params: Dict[str, Any]
) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorTuple]]:
    """Idempotently create a param profile by unique name.

    Returns (result_dict, error_tuple)
    - result_dict: {"id": int, "existed": bool}
    - error_tuple: (code, message) or None
    """
    if not isinstance(name, str) or not name.strip():
        return None, _validation_error("name is required")
    if not isinstance(params, dict):
        return None, _validation_error("params must be a dict")

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM ai_param_profile WHERE name = %s LIMIT 1",
                (name,),
            )
            row = cur.fetchone()
            if row:
                return {"id": int(row[0]), "existed": True}, None

            cur.execute(
                """
                INSERT INTO ai_param_profile (name, params_json, is_active)
                VALUES (%s, %s, 1)
                """,
                (name, json.dumps(params, ensure_ascii=False)),
            )
            new_id = int(cur.lastrowid)
            return {"id": new_id, "existed": False}, None
    except mysql.connector.Error as ex:
        return None, _db_error(ex)
    except Exception as ex:  # safety net
        return None, ("UNEXPECTED_ERROR", str(ex))


def get_param_profile_by_name(name: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorTuple]]:
    """Fetch a param profile by name.

    Returns (row_dict, error_tuple) where row_dict contains:
    {"id", "name", "params_json", "is_active", "created_at", "updated_at"}
    """
    if not isinstance(name, str) or not name.strip():
        return None, _validation_error("name is required")

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, params_json, is_active, created_at, updated_at
                FROM ai_param_profile
                WHERE name = %s
                LIMIT 1
                """,
                (name,),
            )
            row = cur.fetchone()
            if not row:
                return None, ("NOT_FOUND", f"param_profile '{name}' not found")

            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row)), None
    except mysql.connector.Error as ex:
        return None, _db_error(ex)
    except Exception as ex:  # safety net
        return None, ("UNEXPECTED_ERROR", str(ex))

def upsert_connection(cursor, name: str, provider: str, base_url: str, api_key_encrypted: str) -> int:
    """Upserts a connection and returns its ID."""
    cursor.execute("SELECT id FROM ai_connection WHERE name = %s LIMIT 1", (name,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE ai_connection SET provider=%s, base_url=%s, api_key_encrypted=%s, is_active=1 WHERE id=%s",
            (provider, base_url, api_key_encrypted, int(row[0])),
        )
        return int(row[0])
    cursor.execute(
        "INSERT INTO ai_connection(name,provider,base_url,api_key_encrypted,is_active) VALUES(%s,%s,%s,%s,1)",
        (name, provider, base_url, api_key_encrypted),
    )
    return int(cursor.lastrowid)

def upsert_model(cursor, name: str, connection_id: int) -> int:
    """Upserts a model and returns its ID."""
    cursor.execute("SELECT id FROM ai_model WHERE name = %s LIMIT 1", (name,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE ai_model SET connection_id=%s, is_active=1 WHERE id=%s", (connection_id, int(row[0])))
        return int(row[0])
    cursor.execute(
        "INSERT INTO ai_model(name,connection_id,is_active) VALUES(%s,%s,1)", (name, connection_id)
    )
    return int(cursor.lastrowid)

def upsert_param_profile(cursor, name: str, params: Dict[str, Any]) -> int:
    """Upserts a parameter profile and returns its ID."""
    cursor.execute("SELECT id FROM ai_param_profile WHERE name = %s LIMIT 1", (name,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE ai_param_profile SET params_json=%s, is_active=1 WHERE id=%s", (json.dumps(params, ensure_ascii=False), int(row[0])))
        return int(row[0])
    cursor.execute(
        "INSERT INTO ai_param_profile(name,params_json,is_active) VALUES(%s,%s,1)", (name, json.dumps(params, ensure_ascii=False))
    )
    return int(cursor.lastrowid)

def upsert_prompt(cursor, name: str, version: str, messages: Any, response_format: Dict[str, Any], variables: Dict[str, Any]) -> int:
    """Upserts a prompt and returns its ID."""
    cursor.execute("SELECT id FROM ai_prompt WHERE name=%s AND version=%s LIMIT 1", (name, version))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            "UPDATE ai_prompt SET messages_json=%s, response_format_json=%s, variables_json=%s, status='active' WHERE id=%s",
            (json.dumps(messages, ensure_ascii=False), json.dumps(response_format, ensure_ascii=False), json.dumps(variables, ensure_ascii=False), int(row[0]))
        )
        return int(row[0])
    cursor.execute(
        "INSERT INTO ai_prompt(name,version,description,messages_json,response_format_json,variables_json,status) VALUES(%s,%s,%s,%s,%s,%s,'active')",
        (name, version, f"{name} {version}", json.dumps(messages, ensure_ascii=False), json.dumps(response_format, ensure_ascii=False), json.dumps(variables, ensure_ascii=False))
    )
    return int(cursor.lastrowid)


def upsert_config(cursor, config: Dict[str, Any]) -> None:
    """Upserts a config."""
    print(f"Upserting config: {config['config_key']}")
    
    # Get foreign keys, ensuring the cursor is cleared after each fetch
    cursor.execute("SELECT id FROM ai_model WHERE name = %s", (config['model_name'],))
    model_row = cursor.fetchone()
    if not model_row: raise ValueError(f"Model not found: {config['model_name']}")
    model_id = model_row[0]
    
    # In mysql-connector-python, results must be fully read before next query
    cursor.fetchall()

    cursor.execute("SELECT id FROM ai_prompt WHERE name = %s AND version = %s", (config['prompt_name'], config['prompt_version']))
    prompt_row = cursor.fetchone()
    if not prompt_row: raise ValueError(f"Prompt not found: {config['prompt_name']} v{config['prompt_version']}")
    prompt_id = prompt_row[0]
    cursor.fetchall()

    cursor.execute("SELECT id FROM ai_param_profile WHERE name = %s", (config['param_profile_name'],))
    param_row = cursor.fetchone()
    if not param_row: raise ValueError(f"Param profile not found: {config['param_profile_name']}")
    param_profile_id = param_row[0]
    cursor.fetchall()

    sql = """
        INSERT INTO ai_config (config_key, description, model_id, prompt_id, param_profile_id, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        description = VALUES(description),
        model_id = VALUES(model_id),
        prompt_id = VALUES(prompt_id),
        param_profile_id = VALUES(param_profile_id),
        is_active = VALUES(is_active);
    """
    cursor.execute(sql, (
        config['config_key'],
        config.get('description'),
        model_id,
        prompt_id,
        param_profile_id,
        config.get('is_active', 1)
    ))

# Note: upsert_connection is not in the temp script, will add a placeholder if needed by cfg_tool.
def upsert_connection(cursor, connection: Dict[str, Any]) -> None:
    """Placeholder for upserting a connection."""
    # This function is required by cfg_tool but its logic is not in the upsert script.
    # Add implementation based on ai_connection table schema if needed.
    print(f"Placeholder: Upserting connection: {connection.get('provider')}")
    pass

