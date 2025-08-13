from __future__ import annotations

import os
import time
from typing import Any, Optional
from ..runtime import get_current_task_id, get_current_session_id

import httpx


def server_base_url() -> str:
    return os.getenv("UAI_BASE_URL", "http://localhost:8000").rstrip("/")


def post_wait(task_id: str, prompt: str) -> None:
    try:
        httpx.post(
            f"{server_base_url()}/run/{task_id}/wait",
            json={"prompt": prompt},
            timeout=30,
        )
    except Exception:
        pass


def get_status(task_id: str) -> dict[str, Any] | None:
    try:
        r = httpx.get(f"{server_base_url()}/run/{task_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def poll_for_next_input(
    task_id: str, baseline_index: int, timeout_seconds: int = 300
) -> tuple[str, int]:
    """Poll the server for a new input. Returns (value, new_index)."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        data = get_status(task_id)
        if data:
            buf = data.get("input_buffer") or []
            if isinstance(buf, list) and len(buf) > baseline_index:
                value = str(buf[baseline_index])
                return value, baseline_index + 1
        time.sleep(0.5)
    return "", baseline_index


# Convenience helpers for user adapters/agents
def post_log(task_id: Optional[str], level: str, message: str) -> None:
    task_id = task_id or get_current_task_id() or ""
    if not task_id:
        return
    try:
        httpx.post(
            f"{server_base_url()}/run/{task_id}/logs",
            json={"level": level, "message": message},
            timeout=30,
        )
    except Exception:
        pass


def add_run_artifact(
    task_id: Optional[str], artifact: dict[str, Any]
) -> Optional[dict[str, Any]]:
    task_id = task_id or get_current_task_id() or ""
    if not task_id:
        return None
    try:
        r = httpx.post(
            f"{server_base_url()}/run/{task_id}/artifacts", json=artifact, timeout=60
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def add_chat_artifact(
    session_id: Optional[str], artifact: dict[str, Any]
) -> Optional[dict[str, Any]]:
    session_id = session_id or get_current_session_id() or ""
    if not session_id:
        return None
    try:
        r = httpx.post(
            f"{server_base_url()}/chat/{session_id}/artifacts",
            json=artifact,
            timeout=60,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def request_human_input(
    task_id: Optional[str],
    prompt: str = "Awaiting human input...",
    baseline_index: Optional[int] = None,
) -> tuple[str, int]:
    """Notify server we're waiting for input, then poll until a reply arrives.

    Returns (value, new_baseline_index). If baseline_index is None, it is computed from
    current input_buffer length.
    """
    task_id = task_id or get_current_task_id() or ""
    if not task_id:
        return "", baseline_index or 0
    if baseline_index is None:
        data = get_status(task_id) or {}
        buf = data.get("input_buffer") or []
        baseline_index = len(buf) if isinstance(buf, list) else 0
    post_wait(task_id, prompt)
    return poll_for_next_input(task_id, baseline_index)
