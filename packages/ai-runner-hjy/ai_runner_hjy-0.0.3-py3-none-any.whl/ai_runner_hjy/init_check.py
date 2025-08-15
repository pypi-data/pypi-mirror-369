from __future__ import annotations

import os
import sys
import socket
import tempfile
from typing import Dict, List, Tuple

from .core.config import AppConfig
from .core.db import get_db_connection


def _check_config(config: AppConfig) -> Tuple[bool, str]:
    """Validates the application configuration."""
    try:
        # Pydantic automatically validates on instantiation.
        # If this doesn't throw, the required fields are present.
        return True, "OK"
    except Exception as e:
        return False, str(e)


def _check_db(config: AppConfig) -> Tuple[bool, str]:
    try:
        with get_db_connection(config) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            _ = cur.fetchone()
        return True, "OK"
    except Exception as e:
        return False, f"DB_CONNECT_FAIL: {e}"


def _check_python_and_deps() -> Tuple[bool, str]:
    ok_version = sys.version_info >= (3, 9)
    missing: List[str] = []
    for mod in ("dotenv", "mysql.connector", "httpx", "fastapi", "oss2"):
        try:
            __import__(mod)
        except Exception:
            missing.append(mod)
    if ok_version and not missing:
        return True, "OK"
    msg = []
    if not ok_version:
        msg.append(f"Python>={3}.9 required, got {sys.version.split()[0]}")
    if missing:
        msg.append("missing: " + ", ".join(missing))
    return False, "; ".join(msg)


def _check_tmp_writable() -> Tuple[bool, str]:
    path = os.path.join(os.getcwd(), "tmp")
    try:
        os.makedirs(path, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=path, delete=True) as f:
            f.write(b"ok")
        return True, f"OK ({path})"
    except Exception as e:
        return False, f"TMP_WRITE_FAIL {path}: {e}"


def _find_free_port(start: int = 8899, attempts: int = 50) -> Tuple[bool, int, str]:
    for i in range(attempts):
        port = start + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return True, port, "OK"
            except OSError:
                continue
    return False, start, "NO_FREE_PORT"


def _persist_dev_port(port: int) -> Tuple[bool, str]:
    """Persist DEV_SERVER_PORT in basic.env (idempotent)."""
    env_path = os.path.join(os.getcwd(), "basic.env")
    try:
        lines: List[str] = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        key = "DEV_SERVER_PORT"
        new_line = f"{key}={port}"
        found = False
        for idx, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[idx] = new_line
                found = True
                break
        if not found:
            lines.append(new_line)
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return True, f"saved to basic.env ({port})"
    except Exception as e:
        return False, f"SAVE_FAIL: {e}"


def run_init(
    config: AppConfig,
    env_only: bool = False, 
    db_only: bool = False, 
    dev_port: int | None = None
) -> int:
    results: Dict[str, str] = {}

    # Env check
    if not db_only:
        ok_env, env_msg = _check_config(config)
        results["config"] = "OK" if ok_env else f"FAIL: {env_msg}"
        ok_py, py_msg = _check_python_and_deps()
        results["python_deps"] = "OK" if ok_py else f"WARN: {py_msg}"
        ok_tmp, tmp_msg = _check_tmp_writable()
        results["tmp"] = "OK" if ok_tmp else f"WARN: {tmp_msg}"

    # DB check
    if not env_only:
        ok_db, db_msg = _check_db(config)
        results["db"] = "OK" if ok_db else f"FAIL: {db_msg}"

    # Port probing & persist
    if dev_port is not None:
        ok_port, port, port_msg = _find_free_port(start=dev_port)
        if ok_port:
            ok_save, save_msg = _persist_dev_port(port)
            results["dev_port"] = f"OK {port} ({save_msg})"
        else:
            results["dev_port"] = f"FAIL: {port_msg}"

    # Print summary
    print("=== ai-runner-hjy init summary ===")
    for k, v in results.items():
        print(f"{k}: {v}")

    # decide exit code: FAIL if env or db failed
    if results.get("config", "OK").startswith("FAIL") or results.get("db", "OK").startswith("FAIL"):
        return 1
    return 0

