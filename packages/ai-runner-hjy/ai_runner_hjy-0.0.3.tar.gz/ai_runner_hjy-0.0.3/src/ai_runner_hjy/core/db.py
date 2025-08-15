import os
import mysql.connector
from typing import Optional, Tuple, Dict, Any
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from .config import AppConfig, logger
from .errors import AiConnectionError


def get_db_connection(config: AppConfig, db_name: Optional[str] = None) -> MySQLConnection:
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=config.mysql_host,
            port=config.mysql_port,
            user=config.mysql_user,
            password=config.mysql_password,
            database=db_name or config.mysql_ai_database,
            ssl_disabled=True,  # Assuming SSL should be disabled based on old logic
        )
        if connection.is_connected():
            logger.debug("Database connection successful.")
            return connection
    except Error as e:
        logger.error(f"Error while connecting to MySQL: {e}")
        raise AiConnectionError(f"MySQL connect failed: {e}")
    
    # This part should not be reached if an exception is raised
    raise Error("Failed to connect to the database and no exception was caught.")


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

