from __future__ import annotations

import json
from typing import Any, Dict, List

from ..core.config import AppConfig
from ..core.db import get_db_connection
from ..cfg_tool import (
    upsert_connection,
    upsert_model,
    upsert_param_profile,
    upsert_prompt,
    upsert_config,
)


class FullstackGenError(RuntimeError):
    pass


def _expect(obj: Dict[str, Any], key: str) -> Any:
    if key not in obj:
        raise FullstackGenError(f"missing required key: {key}")
    return obj[key]


def generate_fullstack_from_yaml_dict(data: Dict[str, Any], config: AppConfig) -> List[str]:
    """End-to-end upsert based on a richer YAML schema.

    Supported top-level keys:
      - connections: [{ name, provider, base_url, api_key_plain }]
      - models: [{ name, connection: <name> }]
      - param_profiles: [{ name, params: {...} }]
      - prompts: [{ name, version, messages, response_format, variables }]
      - configs: [{ config_key, model: <name>, param_profile: <name>, prompt: <name>@<version>, description }]

    Returns a list of human-readable change summaries.
    """
    changes: List[str] = []

    connections = data.get("connections", []) or []
    models = data.get("models", []) or []
    param_profiles = data.get("param_profiles", []) or []
    prompts = data.get("prompts", []) or []
    configs = data.get("configs", []) or []

    # short-circuit if user passed legacy schema (ids on configs)
    if configs and isinstance(configs[0], dict) and (
        "model_id" in configs[0] or "param_profile_id" in configs[0] or "prompt_id" in configs[0]
    ) and not (connections or models or param_profiles or prompts):
        # let legacy flow be handled by cfg_tool.generate_configs_from_yaml
        return changes

    name_to_connection_id: Dict[str, int] = {}
    name_to_model_id: Dict[str, int] = {}
    name_to_param_id: Dict[str, int] = {}
    prompt_key_to_id: Dict[str, int] = {}

    with get_db_connection(config) as conn:
        with conn.cursor() as cur:
            # connections
            for c in connections:
                name = _expect(c, "name")
                provider = _expect(c, "provider")
                base_url = _expect(c, "base_url")
                api_key_plain = _expect(c, "api_key_plain")
                cid = upsert_connection(cur, name, provider, base_url, api_key_plain, config)
                name_to_connection_id[name] = cid
                changes.append(f"upsert connection: {name}")

            # models
            for m in models:
                name = _expect(m, "name")
                conn_name = _expect(m, "connection")
                if conn_name not in name_to_connection_id:
                    raise FullstackGenError(f"unknown connection: {conn_name}")
                mid = upsert_model(cur, name, name_to_connection_id[conn_name])
                name_to_model_id[name] = mid
                changes.append(f"upsert model: {name}")

            # param profiles
            for p in param_profiles:
                name = _expect(p, "name")
                params = _expect(p, "params")
                pid = upsert_param_profile(cur, name, params)
                name_to_param_id[name] = pid
                changes.append(f"upsert param_profile: {name}")

            # prompts
            for pr in prompts:
                name = _expect(pr, "name")
                version = _expect(pr, "version")
                messages = _expect(pr, "messages")
                response_format = pr.get("response_format") or {}
                variables = pr.get("variables") or {}
                prid = upsert_prompt(cur, name, version, messages, response_format, variables)
                prompt_key = f"{name}@{version}"
                prompt_key_to_id[prompt_key] = prid
                changes.append(f"upsert prompt: {prompt_key}")

            # configs (by names)
            for cfg in configs:
                cfg_key = _expect(cfg, "config_key")
                model_name = _expect(cfg, "model")
                param_name = _expect(cfg, "param_profile")
                prompt_ref = _expect(cfg, "prompt")  # "name@version"
                description = cfg.get("description", "")

                if model_name not in name_to_model_id:
                    raise FullstackGenError(f"unknown model: {model_name}")
                if param_name not in name_to_param_id:
                    raise FullstackGenError(f"unknown param_profile: {param_name}")
                if prompt_ref not in prompt_key_to_id:
                    raise FullstackGenError(f"unknown prompt: {prompt_ref}")

                cfg_id = upsert_config(
                    cur,
                    cfg_key,
                    name_to_model_id[model_name],
                    name_to_param_id[param_name],
                    prompt_key_to_id[prompt_ref],
                    description,
                )
                changes.append(f"upsert config: {cfg_key}")

        conn.commit()

    return changes

