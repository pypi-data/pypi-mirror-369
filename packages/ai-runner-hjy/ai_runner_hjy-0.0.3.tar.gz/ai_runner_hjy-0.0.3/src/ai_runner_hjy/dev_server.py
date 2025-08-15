from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .core.config import AppConfig, get_config
from .core.routing import resolve_route, RouteResolutionError
from .core.request import post_with_retry
from .core.db import get_db_connection

def create_dev_app(config: AppConfig) -> FastAPI:
    app = FastAPI(
        title="AI Runner Hjy - Dev Sandbox",
        description="An interactive server to test ai-runner-hjy routes.",
        version="0.0.2",
    )
    app.state.config = config

    # mount static and index route for the running app
    _static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(_static_dir):
        app.mount("/static", StaticFiles(directory=_static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def _index():
        index_path = os.path.join(_static_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(f.read())
        return HTMLResponse("<h3>Dev server is running</h3>")


    @app.get("/routes")
    async def list_routes(request: Request, project: Optional[str] = None):
        if not project:
            return {"routes": []}
        rows = []
        try:
            config: AppConfig = request.app.state.config
            with get_db_connection(config) as conn:
                cur = conn.cursor()
                cur.execute(
                """
                SELECT r.route_key, r.policy
                FROM ai_route_v2 r
                JOIN ai_project_v2 p ON p.id=r.project_id
                WHERE p.name=%s AND r.is_active=1
                ORDER BY r.id DESC
                """,
                (project,),
            )
                rows = cur.fetchall() or []
        except Exception:
            rows = []
        return {"routes": [{"route_key": rk, "policy": pol} for (rk, pol) in rows]}

    def _mask_headers(headers: Dict[str, str]) -> Dict[str, str]:
        out = dict(headers or {})
        auth = out.get("Authorization")
        if isinstance(auth, str) and len(auth) > 14:
            out["Authorization"] = auth[:10] + "***" + auth[-3:]
        return out


    @app.post("/invoke")
    async def invoke_route(request: Request):
        """Single entry for web sandbox.

        Body accepts: { project_name, route_key, variables, dry_run }
        Returns dry-run preview (request+meta) or real run result with duration.
        """
        body = await request.json()
        project_name = body.get("project_name") or body.get("project")  # tolerate old key
        route_key = body.get("route_key") or body.get("route")
        variables = body.get("variables") or body.get("runtime_variables")
        dry_run = bool(body.get("dry_run"))

        if not project_name or not route_key:
            raise HTTPException(status_code=400, detail="project_name and route_key are required.")

        config: AppConfig = request.app.state.config
        # Build request first (for both dry run and real run)
        try:
            url, headers, req_body, meta = resolve_route(project_name, route_key, config, runtime_variables=variables)
        except RouteResolutionError as e:
            raise HTTPException(status_code=404, detail=str(e))

        if dry_run:
            # Backward-compatible dry-run preview. Keep top-level "headers" for older callers
            # while also returning the full request structure.
            masked = _mask_headers(headers)
            return {
                "dry_run": True,
                "headers": masked,
                "request": {"url": url, "headers": masked, "body": req_body},
                "meta": meta,
            }

        # Real run
        t0 = time.monotonic()
        status, resp_json, error = post_with_retry(url, headers, req_body)
        duration_ms = int((time.monotonic() - t0) * 1000)

        return {
            "status": status,
            "duration_ms": duration_ms,
            "request": {"url": url, "headers": _mask_headers(headers), "body": req_body},
            "meta": meta,
            "response": resp_json,
            "error": error,
        }
    return app


def run_dev_server(config: AppConfig, host: str, port: int):
    """Starts the development server (HMAC disabled)."""
    app = create_dev_app(config)
    uvicorn.run(app, host=host, port=port)


def create_app() -> FastAPI:
    """Factory for tests to import a ready app (HMAC disabled)."""
    config = get_config()
    return create_dev_app(config)

