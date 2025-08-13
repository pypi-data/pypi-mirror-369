import os
import mysql.connector
from typing import Optional, Tuple, Dict, Any


def get_db_connection(database: Optional[str] = None):
    cfg_db = database or os.getenv("MYSQL_AI_DATABASE") or os.getenv("MYSQL_DATABASE")
    if not cfg_db:
        raise RuntimeError("MYSQL_AI_DATABASE or MYSQL_DATABASE must be set")
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=cfg_db,
        autocommit=True,
        ssl_disabled=False,
    )


def get_user_and_key_id_by_ak(cur, ak: str) -> Tuple[Optional[int], Optional[int]]:
    cur.execute(
        "SELECT k.id, k.user_id FROM ai_user_key k WHERE k.access_key_id=%s AND k.status='active' LIMIT 1",
        (ak,)
    )
    row = cur.fetchone()
    if not row:
        return None, None
    key_id = int(row[0]); user_id = int(row[1])
    return user_id, key_id


def insert_user_call_log(
    cur,
    *,
    user_id: Optional[int],
    key_id: Optional[int],
    project_name: str,
    route_key: str,
    http_status: Optional[int],
    duration_ms: Optional[int],
    tokens_prompt: Optional[int],
    tokens_completion: Optional[int],
    ai_call_log_id: Optional[int],
    trace_id: Optional[str],
) -> int:
    cur.execute(
        """
        INSERT INTO ai_user_call_log
        (user_id, key_id, project_name, route_key, http_status, duration_ms, tokens_prompt, tokens_completion, ai_call_log_id, trace_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (user_id, key_id, project_name, route_key, http_status, duration_ms, tokens_prompt, tokens_completion, ai_call_log_id, trace_id)
    )
    return int(cur.lastrowid)

