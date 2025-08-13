from typing import Any, Dict, Optional, Tuple
import json
import os
import sys

import loguru
import mysql.connector

# Configure logger
logger = loguru.logger
logger.remove()
logger.add(
    sys.stderr,
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
)


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
               route_key_for_oss: Optional[str] = None) -> None:
    usage = (resp or {}).get("usage") or {}
    response_id = (resp or {}).get("id")
    # Optionally spill large JSONs to OSS as public links
    req_json_str = _safe_json_dump(request_body)
    resp_json_str = _safe_json_dump(resp)
    if _OSS_ENABLED and route_key_for_oss and _OSS_TRY:
        try:
            from .oss import put_public_json
            if request_body is not None:
                req_url = put_public_json(route_key_for_oss, request_body)
                req_json_str = _safe_json_dump({"oss": req_url})
            if resp is not None:
                resp_url = put_public_json(route_key_for_oss, resp)
                resp_json_str = _safe_json_dump({"oss": resp_url})
        except Exception:
            # best-effort; fall back to inline JSON strings
            pass

    try:
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
        pass

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

