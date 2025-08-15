from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from .core.routing import _fetch_route_row, _compose_row_for_member
from .core.request import post_with_retry, enforce_json_content, validate_no_english_in_values
from .core.logs import insert_log
from ai_runner_hjy.core import db
from .core.config import AppConfig


def resolve_route(project: str, route_key: str, config: AppConfig, runtime_variables: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, str], Dict[str, Any], Dict[str, Any]]:
    """Build a single request for a route.

    Returns: (url, headers, body, meta={"config_key": ...})
    """
    import json as _json
    route_row, members = _fetch_route_row(project, route_key, config)
    if not members:
        raise RuntimeError("No active route members")
    member = members[0]
    composed = _compose_row_for_member(route_row, member)
    if runtime_variables:
        try:
            existing_vars = composed.get("variables_json")
            if isinstance(existing_vars, str):
                existing_vars = _json.loads(existing_vars)
        except Exception:
            existing_vars = {}
        if not isinstance(existing_vars, dict):
            existing_vars = {}
        composed["variables_json"] = {**existing_vars, **runtime_variables}

    from .core.build import build_request_from_row
    url, headers, body = build_request_from_row(composed)
    return url, headers, body, {"config_key": member.get("config_key")}


def run_route(project: str, route_key: str, config: AppConfig, runtime_variables: Optional[Dict[str, Any]] = None) -> Tuple[int, Optional[Dict[str, Any]]]:
    """Run a route once and record the AI call log.

    Returns: (status, response_json)
    """
    import time as _t
    try:
        url, headers, body, meta = resolve_route(project, route_key, config, runtime_variables=runtime_variables)
    except Exception as e:
        # fallback error shape
        return 500, {"error": {"code": "ROUTE_RESOLVE_ERROR", "message": f"unable to resolve route: {e}"}}

    t0 = _t.monotonic()
    trace_id = __import__("uuid").uuid4().hex
    headers = {**headers, "X-Trace-Id": trace_id}

    status, resp_json, error = post_with_retry(url, headers, body)
    duration_ms = int((_t.monotonic() - t0) * 1000)

    enforced, enforcement_error = enforce_json_content({"response_format_json": body.get("response_format")}, resp_json)
    if enforcement_error is None and enforced is not None:
        resp_json = enforced
        letter_err = validate_no_english_in_values({"response_format_json": body.get("response_format")}, resp_json)
        if letter_err is not None:
            error = letter_err

    # Insert AI call log (best-effort)
    conn = None
    try:
        conn = db.get_db_connection(config)
        if conn:
            cur = conn.cursor()
            log_body = {**body, "_trace_id": trace_id}
            insert_log(cur, meta.get("config_key") or route_key, status, duration_ms, resp_json, error, log_body, route_key_for_oss=route_key, config=config)
            conn.commit()
    except Exception as e:
        # Avoid crashing the main flow if logging fails
        __import__("loguru").logger.warning(f"Failed to log AI call: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

    return status, resp_json

