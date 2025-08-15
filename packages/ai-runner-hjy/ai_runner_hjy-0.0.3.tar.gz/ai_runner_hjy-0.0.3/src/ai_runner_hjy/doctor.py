from __future__ import annotations

import os
import socket
from typing import List, Optional

from .core.config import get_config, validate_required_fields, AppConfig
from .core.db import get_db_connection


def _check_env(required: List[str]) -> List[str]:
    missing = []
    for k in required:
        if not (os.environ.get(k) or os.environ.get(k.lower()) or os.environ.get(k.upper())):
            missing.append(k)
    return missing


def _check_tcp(host: str, port: int, timeout_sec: float = 3.0) -> Optional[str]:
    try:
        with socket.create_connection((host, int(port)), timeout=timeout_sec):
            return None
    except Exception as e:
        return str(e)


def run_doctor(env_only: bool = False, db_only: bool = False, timeout_sec: float = 3.0) -> int:
    """
    One-shot diagnostics for env and RDS connectivity.

    - Validates required envs
    - Attempts TCP connectivity to MYSQL_HOST:MYSQL_PORT
    - Attempts DB connection and simple query

    Exit codes: 0=OK, 1=issues found, 2=invalid usage
    """
    if env_only and db_only:
        print("Invalid usage: --env-only and --db-only cannot be used together.")
        return 2

    issues: List[str] = []

    # ENV checks
    if not db_only:
        required_envs = [
            "MYSQL_HOST",
            "MYSQL_PORT",
            "MYSQL_USER",
            "MYSQL_PASSWORD",
            "MYSQL_AI_DATABASE",
            "AI_PEPPER",
        ]
        missing = _check_env(required_envs)
        if missing:
            issues.append(f"Missing required envs: {', '.join(missing)}")

        try:
            cfg = get_config()
            validate_required_fields(cfg)
        except Exception as e:
            issues.append(f"Config validation failed: {e}")

    # DB checks
    if not env_only:
        try:
            cfg = get_config()
            # TCP first
            if cfg.mysql_host and cfg.mysql_port:
                tcp_err = _check_tcp(cfg.mysql_host, cfg.mysql_port, timeout_sec=timeout_sec)
                if tcp_err:
                    issues.append(f"TCP connect to {cfg.mysql_host}:{cfg.mysql_port} failed: {tcp_err}")

            # DB connect and simple query
            with get_db_connection(cfg) as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                _ = cur.fetchone()
        except Exception as e:
            issues.append(f"DB connectivity check failed: {e}")

    if issues:
        print("Doctor results: ISSUES FOUND")
        for i in issues:
            print(f" - {i}")
        print("Suggested actions:")
        print(" - Ensure mysql.env is loaded: set -a; source mysql.env; set +a")
        print(" - Verify network reachability and security groups/whitelists for the DB endpoint")
        print(" - Confirm user has SELECT permission for the target database")
        return 1

    print("Doctor results: OK")
    return 0


