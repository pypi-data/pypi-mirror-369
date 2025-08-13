from __future__ import annotations

import importlib
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Iterator, Optional, Tuple

from .frameworks.utils import post_log


def _truncate(value: Any, limit: int = 1000) -> str:
    try:
        s = repr(value)
    except Exception:
        s = f"<unrepr {type(value).__name__}>"
    if len(s) > limit:
        return s[: limit - 3] + "..."
    return s


def _resolve_owner_attr_from_str(path: str) -> Tuple[Any, str, Callable[..., Any]]:
    """Resolve a dotted path of form 'module:attr.subattr[.method]' to (owner, name, fn)."""
    if ":" not in path:
        raise ValueError("target must be 'module:attr' format")
    mod_name, attr_path = path.split(":", 1)
    mod = importlib.import_module(mod_name)
    parts = attr_path.split(".")
    owner: Any = mod
    for p in parts[:-1]:
        owner = getattr(owner, p)
    name = parts[-1]
    fn = getattr(owner, name)
    if not callable(fn):  # pragma: no cover - defensive
        raise TypeError(f"Attribute '{name}' at '{path}' is not callable")
    return owner, name, fn


def _resolve_owner_attr_from_callable(fn: Callable[..., Any]) -> Tuple[Any, str]:
    """Resolve owner and attribute name for a callable without re-importing its module.

    This avoids ambiguity with short module names (e.g., many examples use module name 'app').
    """
    import sys

    mod_name = getattr(fn, "__module__", None)
    qualname = getattr(fn, "__qualname__", getattr(fn, "__name__", None))
    if not mod_name or not qualname:
        raise ValueError("Cannot resolve owner for callable; pass 'module:attr' string")

    # Start from the live module object if available; otherwise, use function globals
    owner: Any = sys.modules.get(mod_name) or getattr(fn, "__globals__", {})
    parts = qualname.split(".")
    for p in parts[:-1]:
        try:
            owner = getattr(owner, p)
        except Exception:
            # Fallback if owner is a dict-like globals mapping during import time
            if isinstance(owner, dict) and p in owner:
                owner = owner[p]
            else:
                raise AttributeError(
                    f"Cannot resolve owner '{p}' for callable with qualname '{qualname}'"
                )
    return owner, parts[-1]


def _make_wrapper(
    fn: Callable[..., Any], label: Optional[str], capture_return: bool
) -> Callable[..., Any]:
    lbl = label or getattr(fn, "__qualname__", getattr(fn, "__name__", "<call>"))

    @wraps(fn)
    def _wrapped(*args: Any, **kwargs: Any):
        try:
            post_log(
                None,
                "DEBUG",
                f"[{lbl}] call args={_truncate(args)} kwargs={_truncate(kwargs)}",
            )
        except Exception:
            pass
        try:
            result = fn(*args, **kwargs)
        except Exception as e:  # log and re-raise
            try:
                post_log(None, "ERROR", f"[{lbl}] error: {e!r}")
            except Exception:
                pass
            raise
        try:
            if capture_return:
                post_log(None, "DEBUG", f"[{lbl}] return={_truncate(result)}")
            else:
                post_log(None, "DEBUG", f"[{lbl}] done")
        except Exception:
            pass
        return result

    return _wrapped


@contextmanager
def patch_function(
    target: str | Callable[..., Any],
    *,
    label: Optional[str] = None,
    capture_return: bool = False,
) -> Iterator[None]:
    """Temporarily patch a function or method to auto-log its calls.

    - target: either a callable or a string 'module:attr[.subattr...]'.
    - label: optional label to include in logs (defaults to function qualname).
    - capture_return: log the returned value (truncated) when True.
    """
    if isinstance(target, str):
        owner, name, fn = _resolve_owner_attr_from_str(target)
    elif callable(target):
        owner, name = _resolve_owner_attr_from_callable(target)
        fn = getattr(owner, name)
    else:  # pragma: no cover - defensive
        raise TypeError("target must be a callable or 'module:attr' string")

    wrapper = _make_wrapper(fn, label, capture_return)
    orig = getattr(owner, name)
    setattr(owner, name, wrapper)
    try:
        yield
    finally:
        setattr(owner, name, orig)


@contextmanager
def patch_many(
    *targets: str | Callable[..., Any],
    label: Optional[str] = None,
    capture_return: bool = False,
) -> Iterator[None]:
    """Patch multiple targets within a single context.

    Example:
        with patch_many("module:func", SomeClass.method, capture_return=True):
            ...
    """
    patched: list[tuple[Any, str, Any]] = []
    try:
        for t in targets:
            if isinstance(t, str):
                owner, name, fn = _resolve_owner_attr_from_str(t)
            else:
                owner, name = _resolve_owner_attr_from_callable(t)  # type: ignore[arg-type]
                fn = getattr(owner, name)
            wrapper = _make_wrapper(fn, label, capture_return)
            orig = getattr(owner, name)
            setattr(owner, name, wrapper)
            patched.append((owner, name, orig))
        yield
    finally:
        for owner, name, orig in reversed(patched):
            setattr(owner, name, orig)


# Persistent patch registry for convenience patching
_PATCH_REGISTRY: dict[tuple[int, str], Any] = {}


def patch_log(
    target: str | Callable[..., Any],
    *,
    label: Optional[str] = None,
    capture_return: bool = False,
) -> None:
    """Persistently patch a function or method to auto-log its calls.

    Usage: from unified_agent_interface.utils import patch_log; patch_log(ChatOpenAI.invoke)
    """
    if isinstance(target, str):
        owner, name, fn = _resolve_owner_attr_from_str(target)
    elif callable(target):
        owner, name = _resolve_owner_attr_from_callable(target)
        fn = getattr(owner, name)
    else:  # pragma: no cover - defensive
        raise TypeError("target must be a callable or 'module:attr' string")
    key = (id(owner), name)
    if key in _PATCH_REGISTRY:
        return  # already patched
    wrapper = _make_wrapper(fn, label, capture_return)
    orig = getattr(owner, name)
    setattr(owner, name, wrapper)
    _PATCH_REGISTRY[key] = orig


def unpatch_log(target: str | Callable[..., Any]) -> None:
    """Restore an item patched via patch_log."""
    if isinstance(target, str):
        owner, name, _ = _resolve_owner_attr_from_str(target)
    elif callable(target):
        owner, name = _resolve_owner_attr_from_callable(target)
    else:  # pragma: no cover - defensive
        raise TypeError("target must be a callable or 'module:attr' string")
    key = (id(owner), name)
    orig = _PATCH_REGISTRY.pop(key, None)
    if orig is not None:
        setattr(owner, name, orig)
