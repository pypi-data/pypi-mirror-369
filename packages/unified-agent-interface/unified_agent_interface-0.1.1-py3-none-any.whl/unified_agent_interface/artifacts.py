from __future__ import annotations

import fnmatch
import os
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional, Tuple

from .frameworks.utils import add_chat_artifact, add_run_artifact
from .runtime import get_current_session_id, get_current_task_id


# Context configuration for tracking
_tracking_active: ContextVar[bool] = ContextVar("uai_artifacts_active", default=False)
_include_globs: ContextVar[Tuple[str, ...]] = ContextVar(
    "uai_artifacts_include", default=()
)
_exclude_globs: ContextVar[Tuple[str, ...]] = ContextVar(
    "uai_artifacts_exclude", default=()
)
_base_dir: ContextVar[Optional[str]] = ContextVar(
    "uai_artifacts_base_dir", default=None
)


_seen_lock = threading.Lock()
_seen: set[Tuple[str, str, str]] = set()  # (kind, id, abspath)


def _normalize_path(p: str) -> str:
    try:
        return str(Path(p).resolve())
    except Exception:
        return os.path.abspath(p)


def _matches_filters(
    path: str,
    include: Tuple[str, ...],
    exclude: Tuple[str, ...],
    base_dir: Optional[str],
) -> bool:
    if base_dir:
        try:
            p = Path(path).resolve()
            b = Path(base_dir).resolve()
            # ensure path is within base_dir
            try:
                p.relative_to(b)
            except Exception:
                return False
        except Exception:
            return False
    if include:
        if not any(fnmatch.fnmatch(path, pat) for pat in include):
            return False
    if exclude:
        if any(fnmatch.fnmatch(path, pat) for pat in exclude):
            return False
    return True


def _record_artifact(path: str) -> None:
    tid = get_current_task_id()
    sid = get_current_session_id()
    include = _include_globs.get()
    exclude = _exclude_globs.get()
    base_dir = _base_dir.get()

    abspath = _normalize_path(path)
    if not _matches_filters(abspath, include, exclude, base_dir):
        return

    if tid:
        key = ("run", tid, abspath)
        with _seen_lock:
            if key in _seen:
                return
            _seen.add(key)
        add_run_artifact(
            None,
            {
                "type": "file",
                "name": os.path.basename(abspath),
                "uri": abspath,
                "metadata": {},
            },
        )
    elif sid:
        key = ("chat", sid, abspath)
        with _seen_lock:
            if key in _seen:
                return
            _seen.add(key)
        add_chat_artifact(
            None,
            {
                "type": "file",
                "name": os.path.basename(abspath),
                "uri": abspath,
                "metadata": {},
            },
        )


def _audit_hook(
    event: str, args: tuple[Any, ...]
) -> None:  # pragma: no cover - integration path
    if not _tracking_active.get():
        return
    if event != "open":
        return
    if not (get_current_task_id() or get_current_session_id()):
        return
    # Expecting args: (path, mode, flags)
    path = None
    mode = ""
    flags = 0
    try:
        if args:
            path = args[0]
        if len(args) > 1 and isinstance(args[1], str):
            mode = args[1]
        if len(args) > 2 and isinstance(args[2], int):
            flags = args[2]
    except Exception:
        return
    if not isinstance(path, (str, os.PathLike)):
        return
    # Heuristic: consider as artifact when opening for writing/creating/appending
    create_modes = any(ch in (mode or "") for ch in ("w", "x", "a"))
    create_flags = bool(flags & getattr(os, "O_CREAT", 0))
    if create_modes or create_flags:
        try:
            _record_artifact(str(path))
        except Exception:
            pass


# Register audit hook once
try:  # pragma: no cover - env dependent
    import sys

    sys.addaudithook(_audit_hook)
except Exception:
    pass


@contextmanager
def artifact_tracking_context(
    enabled: bool,
    *,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    base_dir: Optional[str] = None,
) -> Iterator[None]:
    token_active = _tracking_active.set(bool(enabled))
    token_inc = _include_globs.set(tuple(include or ()))
    token_exc = _exclude_globs.set(tuple(exclude or ()))
    token_base = _base_dir.set(base_dir)
    try:
        yield
    finally:
        _tracking_active.reset(token_active)
        _include_globs.reset(token_inc)
        _exclude_globs.reset(token_exc)
        _base_dir.reset(token_base)
