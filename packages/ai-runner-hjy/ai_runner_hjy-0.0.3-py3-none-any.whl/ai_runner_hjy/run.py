import json
import os
import time
from typing import Any, Dict, Optional, Tuple

from .core.config import AppConfig, logger
from .core.db import get_db_connection
from .core.build import build_request_from_row
from .core.request import (
    post_with_retry,
    enforce_json_content,
    validate_no_english_in_values,
)
from .core.logs import insert_log
from uuid import uuid4
from .core.types import RunResult


def run_once(config_key: Optional[str] = None,
             runtime_variables: Optional[Dict[str, Any]] = None,
             config: Optional[AppConfig] = None) -> None:
    """Execute a single config and record logs. Returns None for backward compatibility."""
    if not config:
        from .core.config import get_config
        config = get_config()

    with get_db_connection(config) as conn:
        cur = conn.cursor()
        # fetch_active_config is simple enough to inline here to avoid another module
        if config_key:
            cur.execute(
                """
                SELECT c.base_url, c.api_key_encrypted, m.name AS model_name,
                       pp.params_json, pr.messages_json, pr.response_format_json, pr.variables_json,
                       cfg.config_key
                FROM ai_config cfg
                JOIN ai_model m ON m.id = cfg.model_id
                JOIN ai_connection c ON c.id = m.connection_id
                LEFT JOIN ai_param_profile pp ON pp.id = cfg.param_profile_id
                LEFT JOIN ai_prompt pr ON pr.id = cfg.prompt_id
                WHERE cfg.is_active = 1 AND cfg.config_key = %s
                LIMIT 1
                """,
                (config_key,),
            )
        else:
            cur.execute(
                """
                SELECT c.base_url, c.api_key_encrypted, m.name AS model_name,
                       pp.params_json, pr.messages_json, pr.response_format_json, pr.variables_json,
                       cfg.config_key
                FROM ai_config cfg
                JOIN ai_model m ON m.id = cfg.model_id
                JOIN ai_connection c ON c.id = m.connection_id
                LEFT JOIN ai_param_profile pp ON pp.id = cfg.param_profile_id
                LEFT JOIN ai_prompt pr ON pr.id = cfg.prompt_id
                WHERE cfg.is_active = 1
                ORDER BY cfg.id ASC
                LIMIT 1
                """
            )
        row = cur.fetchone()
        if not row:
            raise RuntimeError("CONFIG_NOT_FOUND")
        cols = [d[0] for d in cur.description]
        row_dict = dict(zip(cols, row))

        # Merge runtime variables (e.g., AUDIO_URL/AUDIO_FORMAT) into variables_json before building
        if runtime_variables:
            try:
                existing_vars = row_dict.get("variables_json")
                if isinstance(existing_vars, str):
                    existing_vars = json.loads(existing_vars)
                if not isinstance(existing_vars, dict):
                    existing_vars = {}
                merged_vars = {**existing_vars, **runtime_variables}
                row_dict["variables_json"] = merged_vars
            except Exception:
                row_dict["variables_json"] = runtime_variables

        url, headers, body = build_request_from_row(row_dict, config=config)
        trace_id = uuid4().hex
        # add trace id header (safe for providers) and enrich log body only
        headers = {**headers, "X-Trace-Id": trace_id}
        log_body = {**body, "_trace_id": trace_id}
        cfg_key = row_dict["config_key"]

        logger.info("Sending request to AI provider: config_key={} model={}", cfg_key, body.get("model"))
        t0 = time.monotonic()

        # Content-level retry up to 3 times when JSON invalid or English letters detected
        status: int = 0
        resp_json: Optional[Dict[str, Any]] = None
        error: Optional[Tuple[str, str]] = None
        # Max retries = 3 means up to 4 total attempts (initial + 3 retries)
        max_content_retries = 3
        for attempt in range(max_content_retries + 1):
            status, resp_json, error = post_with_retry(url, headers, body, timeout=config.ai_timeout)
            if error is None and resp_json is not None:
                # enforce json if requested
                enforced, enforcement_error = enforce_json_content(row_dict, resp_json)
                if enforcement_error is None and enforced is not None:
                    resp_json = enforced
                    # Validate no English letters in any string field
                    letter_err = validate_no_english_in_values(row_dict, resp_json)
                    if letter_err is None:
                        # Valid content
                        break
                    else:
                        error = letter_err
                else:
                    error = enforcement_error

            # Decide whether to retry on content/structure errors
            if error and error[0] in {"SCHEMA_INVALID", "LETTER_DETECTED"} and attempt < max_content_retries:
                logger.warning("Content validation failed ({}). Retrying {}/{}...", error[0], attempt + 1, max_content_retries)
                time.sleep(1) # simple 1s delay before content retry
                continue
            # For network/HTTP errors (already retried inside post_with_retry) or last attempt, stop
            break

        duration_ms = int((time.monotonic() - t0) * 1000)
        insert_log(cur, cfg_key, status, duration_ms, resp_json, error, log_body, config=config)

        if resp_json:
            try:
                choice = (resp_json.get("choices") or [])[0]
                content = None
                if isinstance(choice, dict):
                    msg = choice.get("message") or {}
                    content = msg.get("content")
                logger.info("AI response: {}", content)
            except Exception:
                logger.info("AI raw response keys: {}", list(resp_json.keys()))
        else:
            logger.warning("No response body. Check logs table for error details.")


def run_once_result(config_key: Optional[str] = None,
                    runtime_variables: Optional[Dict[str, Any]] = None,
                    config: Optional[AppConfig] = None) -> RunResult:
    """Execute a single config and return a structured RunResult (non-breaking new API)."""
    if not config:
        from .core.config import get_config
        config = get_config()

    with get_db_connection(config) as conn:
        cur = conn.cursor()
        if config_key:
            cur.execute(
                """
                SELECT c.base_url, c.api_key_encrypted, m.name AS model_name,
                       pp.params_json, pr.messages_json, pr.response_format_json, pr.variables_json,
                       cfg.config_key
                FROM ai_config cfg
                JOIN ai_model m ON m.id = cfg.model_id
                JOIN ai_connection c ON c.id = m.connection_id
                LEFT JOIN ai_param_profile pp ON pp.id = cfg.param_profile_id
                LEFT JOIN ai_prompt pr ON pr.id = cfg.prompt_id
                WHERE cfg.is_active = 1 AND cfg.config_key = %s
                LIMIT 1
                """,
                (config_key,),
            )
        else:
            cur.execute(
                """
                SELECT c.base_url, c.api_key_encrypted, m.name AS model_name,
                       pp.params_json, pr.messages_json, pr.response_format_json, pr.variables_json,
                       cfg.config_key
                FROM ai_config cfg
                JOIN ai_model m ON m.id = cfg.model_id
                JOIN ai_connection c ON c.id = m.connection_id
                LEFT JOIN ai_param_profile pp ON pp.id = cfg.param_profile_id
                LEFT JOIN ai_prompt pr ON pr.id = cfg.prompt_id
                WHERE cfg.is_active = 1
                ORDER BY cfg.id ASC
                LIMIT 1
                """
            )
        row = cur.fetchone()
        if not row:
            raise RuntimeError("CONFIG_NOT_FOUND")
        cols = [d[0] for d in cur.description]
        row_dict = dict(zip(cols, row))

        if runtime_variables:
            try:
                existing_vars = row_dict.get("variables_json")
                if isinstance(existing_vars, str):
                    existing_vars = json.loads(existing_vars)
                if not isinstance(existing_vars, dict):
                    existing_vars = {}
                merged_vars = {**existing_vars, **runtime_variables}
                row_dict["variables_json"] = merged_vars
            except Exception:
                row_dict["variables_json"] = runtime_variables

        url, headers, body = build_request_from_row(row_dict, config=config)
        trace_id = uuid4().hex
        headers = {**headers, "X-Trace-Id": trace_id}
        log_body = {**body, "_trace_id": trace_id}
        cfg_key = row_dict["config_key"]

        logger.info("Sending request to AI provider: config_key={} model={}", cfg_key, body.get("model"))
        t0 = time.monotonic()

        status: int = 0
        resp_json: Optional[Dict[str, Any]] = None
        error: Optional[Tuple[str, str]] = None
        max_content_retries = 3
        for attempt in range(max_content_retries + 1):
            status, resp_json, error = post_with_retry(url, headers, body, timeout=config.ai_timeout)
            if error is None and resp_json is not None:
                enforced, enforcement_error = enforce_json_content(row_dict, resp_json)
                if enforcement_error is None and enforced is not None:
                    resp_json = enforced
                    letter_err = validate_no_english_in_values(row_dict, resp_json)
                    if letter_err is None:
                        break
                    else:
                        error = letter_err
                else:
                    error = enforcement_error
            if error and error[0] in {"SCHEMA_INVALID", "LETTER_DETECTED"} and attempt < max_content_retries:
                logger.warning("Content validation failed ({}). Retrying {}/{}...", error[0], attempt + 1, max_content_retries)
                time.sleep(1)
                continue
            break

        duration_ms = int((time.monotonic() - t0) * 1000)
        insert_log(cur, cfg_key, status, duration_ms, resp_json, error, log_body, config=config)

        usage = None
        if resp_json and isinstance(resp_json, dict):
            usage = resp_json.get("usage")

        return RunResult(
            status=status,
            duration_ms=duration_ms,
            trace_id=trace_id,
            response=resp_json,
            error=error,
            meta={"config_key": cfg_key},
            usage=usage,
        )
