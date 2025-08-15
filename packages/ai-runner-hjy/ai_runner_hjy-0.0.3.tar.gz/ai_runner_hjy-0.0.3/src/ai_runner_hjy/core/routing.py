from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import mysql.connector

from .db import get_db_connection
from .build import build_request_from_row
from .policy import get_strategy
from .config import AppConfig


class RouteResolutionError(RuntimeError):
    pass


def _fetch_route_row(project: str, route_key: str, config: AppConfig) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Fetch route_v2 and its active members joined to ai_config/connection/model.

    Returns (route_row, members_rows)
    """
    with get_db_connection(config) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT r.id as route_id, r.policy, r.policy_config_json, r.variables_json,
                   r.param_profile_id, r.prompt_id, r.response_format_json
                   , p.name as project_name, r.route_key
            FROM ai_route_v2 r
            JOIN ai_project_v2 p ON p.id=r.project_id
            WHERE p.name=%s AND r.route_key=%s AND r.is_active=1 AND p.status='active'
            LIMIT 1
            """,
            (project, route_key),
        )
        route = cur.fetchone()
        if not route:
            raise RouteResolutionError("ROUTE_NOT_FOUND")
        route_cols = [d[0] for d in cur.description]
        route_row = dict(zip(route_cols, route))

        cur.execute(
            """
            SELECT m.id as member_id, m.priority, m.weight,
                   cfg.id as config_id, cfg.config_key,
                   c.base_url, c.api_key_encrypted,
                   mdl.name as model_name,
                   pp.params_json,
                   pr.messages_json, pr.response_format_json as prompt_response_format_json, pr.variables_json
            FROM ai_route_member_v2 m
            JOIN ai_route_v2 r ON r.id=m.route_id AND m.is_active=1
            JOIN ai_config cfg ON cfg.id=m.config_id AND cfg.is_active=1
            JOIN ai_model mdl ON mdl.id=cfg.model_id
            JOIN ai_connection c ON c.id=mdl.connection_id AND c.is_active=1
            LEFT JOIN ai_param_profile pp ON pp.id=COALESCE(r.param_profile_id, cfg.param_profile_id)
            LEFT JOIN ai_prompt pr ON pr.id=COALESCE(r.prompt_id, cfg.prompt_id)
            WHERE r.id=%s
            ORDER BY m.priority ASC, m.id ASC
            """,
            (route_row["route_id"],),
        )
        members = cur.fetchall()
        member_cols = [d[0] for d in cur.description]
        members_rows = [dict(zip(member_cols, r)) for r in members]
        if not members_rows:
            raise RouteResolutionError("NO_ACTIVE_MEMBERS")

        return route_row, members_rows


def _merge_row(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        out[k] = v
    return out


def _compose_row_for_member(route_row: Dict[str, Any], member_row: Dict[str, Any]) -> Dict[str, Any]:
    # prefer route-level defaults then fall back to member (cfg-derived)
    row: Dict[str, Any] = {
        "base_url": member_row["base_url"],
        "api_key_encrypted": member_row["api_key_encrypted"],
        "model_name": member_row["model_name"],
        "params_json": member_row.get("params_json"),
        "messages_json": member_row.get("messages_json"),
        "response_format_json": route_row.get("response_format_json") or member_row.get("prompt_response_format_json"),
        "variables_json": route_row.get("variables_json") or member_row.get("variables_json"),
    }
    return row


def resolve_route(project: str, route_key: str, config: AppConfig, *, runtime_variables: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, str], Dict[str, Any], Dict[str, Any]]:
    """Resolve a route to concrete request (url, headers, body) using primary_backup first.

    Returns (url, headers, body, chosen_meta)
    chosen_meta includes: {"config_key", "policy", "member_id"}
    """
    route_row, members = _fetch_route_row(project, route_key, config)
    policy = (route_row.get("policy") or "primary_backup").lower()
    selected = get_strategy(policy).select(members, route_row)

    composed = _compose_row_for_member(route_row, selected)

    # merge runtime variables
    if runtime_variables:
        try:
            existing_vars = composed.get("variables_json")
            if isinstance(existing_vars, str):
                existing_vars = json.loads(existing_vars)
        except Exception:
            existing_vars = {}
        if not isinstance(existing_vars, dict):
            existing_vars = {}
        composed["variables_json"] = {**existing_vars, **runtime_variables}

    url, headers, body = build_request_from_row(composed)
    meta = {
        "config_key": selected.get("config_key"),
        "policy": policy,
        "member_id": selected.get("member_id"),
    }
    return url, headers, body, meta

