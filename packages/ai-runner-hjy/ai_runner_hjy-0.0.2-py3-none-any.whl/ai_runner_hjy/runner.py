from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import time

from .core.routing import RouteResolutionError
from .core.request import post_with_retry, enforce_json_content, validate_no_english_in_values
from .providers import DefaultRouteProvider, NoopLogger, RouteProvider, LoggerHook


class RunnerError(Exception):
    """Lightweight runner error to carry a stable code/message pair."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def dry_run(
    project_name: str,
    route_key: str,
    variables: Optional[Dict[str, Any]] = None,
    *,
    route_provider: Optional[RouteProvider] = None,
    logger: Optional[LoggerHook] = None,
) -> Dict[str, Any]:
    """Build a request for the given project/route without calling downstream.

    Returns a preview dict with url, masked headers, body, and meta info.
    Does not perform network I/O or database writes.
    """
    route_provider = route_provider or DefaultRouteProvider()
    logger = logger or NoopLogger()

    try:
        url, headers, body, meta = route_provider.resolve(
            project_name, route_key, runtime_variables=variables or {}
        )
    except RouteResolutionError as e:
        raise RunnerError("ROUTE_RESOLUTION_ERROR", str(e)) from e
    except RuntimeError as e:
        # Strict media validation errors bubble up from build_request_from_row
        msg = str(e)
        if "MISSING_MEDIA_URL" in msg:
            raise RunnerError("MISSING_MEDIA_URL", msg) from e
        raise

    masked_headers = dict(headers)
    auth = masked_headers.get("Authorization")
    if isinstance(auth, str) and len(auth) > 14:
        masked_headers["Authorization"] = auth[:10] + "***" + auth[-3:]

    preview = {
        "url": url,
        "headers": masked_headers,
        "body": body,
        "meta": meta,
    }
    logger.before_call({"phase": "dry_run", "project": project_name, "route": route_key, "meta": meta})
    logger.after_call({"phase": "dry_run", "project": project_name, "route": route_key, "meta": meta})
    return preview


def run(
    project_name: str,
    route_key: str,
    variables: Optional[Dict[str, Any]] = None,
    *,
    route_provider: Optional[RouteProvider] = None,
    logger: Optional[LoggerHook] = None,
) -> Dict[str, Any]:
    """Execute a route with strict validation and return a stable result structure.

    The runner performs:
    - build-time strict media URL validation (no auto-fill)
    - one attempt against the selected member (primary); failover is handled by
      the higher-level route runner in examples/gateway (if desired)
    - JSON response enforcement when response_format is present

    This function avoids DB writes and web framework dependencies by design.
    """
    route_provider = route_provider or DefaultRouteProvider()
    logger = logger or NoopLogger()

    try:
        url, headers, body, meta = route_provider.resolve(
            project_name, route_key, runtime_variables=variables or {}
        )
    except RouteResolutionError as e:
        return _result_error("ROUTE_RESOLUTION_ERROR", str(e))
    except RuntimeError as e:
        msg = str(e)
        if "MISSING_MEDIA_URL" in msg:
            return _result_error("MISSING_MEDIA_URL", msg)
        return _result_error("BUILD_ERROR", msg)

    # inject a trace id for downstream observability
    trace_id = __import__("uuid").uuid4().hex
    headers = {**headers, "X-Trace-Id": trace_id}

    event_ctx = {"project": project_name, "route": route_key, "meta": meta}
    logger.before_call({**event_ctx, "trace_id": trace_id, "phase": "before_call"})

    t0 = time.monotonic()
    status, resp_json, error = post_with_retry(url, headers, body)
    duration_ms = int((time.monotonic() - t0) * 1000)

    # Only enforce JSON schema on successful HTTP responses
    if status == 200:
        enforced, enforcement_error = enforce_json_content(
            {"response_format_json": body.get("response_format")}, resp_json
        )
        if enforcement_error is not None:
            error = enforcement_error
        elif enforced is not None:
            resp_json = enforced
            # optional language gate similar to existing behavior
            letter_err = validate_no_english_in_values(
                {"response_format_json": body.get("response_format")}, resp_json
            )
            if letter_err is not None:
                error = letter_err

    if status == 200 and error is None:
        usage = (resp_json or {}).get("usage") or {}
        result_ok = {
            "status": 200,
            "duration_ms": duration_ms,
            "trace_id": trace_id,
            "response": resp_json,
            "error": None,
            "meta": {**meta, "failover": False},
            "usage": usage,
        }
        logger.after_call({**event_ctx, "trace_id": trace_id, "phase": "after_call", "status": 200, "duration_ms": duration_ms, "usage": usage})
        return result_ok

    # normalize error
    if error is None:
        code, message = "HTTP_ERROR", f"status={status}"
    elif isinstance(error, tuple) and len(error) == 2:
        code, message = error
    else:
        code, message = "DOWNSTREAM_ERROR", str(error)

    result_err = {
        "status": status,
        "duration_ms": duration_ms,
        "trace_id": trace_id,
        "response": resp_json,
        "error": {"code": code, "message": message},
        "meta": {**meta, "failover": False},
        "usage": (resp_json or {}).get("usage") or {},
    }
    logger.after_call({**event_ctx, "trace_id": trace_id, "phase": "after_call", "status": status, "duration_ms": duration_ms, "error": {"code": code, "message": message}})
    return result_err


def _result_error(code: str, message: str) -> Dict[str, Any]:
    return {
        "status": 400 if code == "MISSING_MEDIA_URL" else 500,
        "duration_ms": 0,
        "trace_id": None,
        "response": None,
        "error": {"code": code, "message": message},
        "meta": {"failover": False},
        "usage": {},
    }

