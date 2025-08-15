from typing import Any, Dict, Optional, Tuple
import json
import os
import sys

import mysql.connector

from .config import AppConfig, logger
from .oss import put_public_json


_OSS_ENABLED = os.environ.get("ENABLE_OSS_SPILLOVER", "true").lower() == "true"
_OSS_TRY = os.environ.get("OSS_SPILLOVER_TRY", "true").lower() == "true"


def _safe_json_dump(obj: Any) -> Optional[str]:
    try:
        if obj is None:
            return None
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        try:
            return str(obj)
        except Exception:
            return None


def insert_log(cursor,
               config_key: str,
               http_status: int,
               duration_ms: int,
               resp: Optional[Dict[str, Any]],
               err: Optional[Tuple[str, str]],
               request_body: Optional[Dict[str, Any]] = None,
               *,
               route_key_for_oss: Optional[str] = None,
               config: Optional[AppConfig] = None) -> None:
    
    usage = (resp or {}).get("usage", {})
    if not isinstance(usage, dict):
        usage = {}
    response_id = (resp or {}).get("id")

    req_json_str = _safe_json_dump(request_body)
    resp_json_str = _safe_json_dump(resp)

    # Simplified OSS spillover logic
    if config and config.enable_oss_spillover and route_key_for_oss:
        try:
            if request_body:
                req_json_str = put_public_json(f"{route_key_for_oss}_req", request_body, config=config)
            if resp:
                resp_json_str = put_public_json(f"{route_key_for_oss}_resp", resp, config=config)
        except Exception as e:
            logger.warning(f"OSS spillover failed for {route_key_for_oss}: {e}")
            # Do not fail the log insertion if spillover fails

    try:
        # First attempt to insert with the JSON fields.
        cursor.execute(
            """
            INSERT INTO ai_call_logs
                (config_key, http_status, duration_ms,
                 prompt_tokens, completion_tokens, total_tokens,
                 response_id, error_code, error_message,
                 request_body_json, response_body_json)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                config_key,
                http_status,
                duration_ms,
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                usage.get("total_tokens"),
                response_id,
                err[0] if err else None,
                err[1] if err else None,
                req_json_str,
                resp_json_str,
            ),
        )
        return
    except mysql.connector.Error:
        # This fallback is likely for an older schema without JSON fields.
        # It's kept for compatibility but our main flow now uses the above query.
        logger.warning("Failed to insert log with JSON fields, falling back to old schema.")
        pass

    # Fallback INSERT without JSON fields
    cursor.execute(
        """
        INSERT INTO ai_call_logs
            (config_key, http_status, duration_ms, prompt_tokens, completion_tokens, total_tokens, response_id, error_code, error_message)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            config_key,
            http_status,
            duration_ms,
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
            usage.get("total_tokens"),
            response_id,
            err[0] if err else None,
            err[1] if err else None,
        ),
    )

