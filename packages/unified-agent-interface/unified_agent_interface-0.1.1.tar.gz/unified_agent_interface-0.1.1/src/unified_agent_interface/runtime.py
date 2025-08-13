from __future__ import annotations

from contextvars import ContextVar
from contextlib import contextmanager
from typing import Iterator, Optional


_current_task_id: ContextVar[Optional[str]] = ContextVar(
    "uai_current_task_id", default=None
)
_current_session_id: ContextVar[Optional[str]] = ContextVar(
    "uai_current_session_id", default=None
)


def get_current_task_id() -> Optional[str]:
    return _current_task_id.get()


def get_current_session_id() -> Optional[str]:
    return _current_session_id.get()


@contextmanager
def task_context(task_id: Optional[str]) -> Iterator[None]:
    token = _current_task_id.set(task_id)
    try:
        yield
    finally:
        _current_task_id.reset(token)


@contextmanager
def session_context(session_id: Optional[str]) -> Iterator[None]:
    token = _current_session_id.set(session_id)
    try:
        yield
    finally:
        _current_session_id.reset(token)
