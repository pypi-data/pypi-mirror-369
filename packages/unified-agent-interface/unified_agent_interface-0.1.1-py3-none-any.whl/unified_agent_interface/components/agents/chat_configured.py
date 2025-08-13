from __future__ import annotations

from typing import Any, Dict, Tuple, List

from .base import Agent
from ...config import AgentConfig
from ...models.chat import Artifact, Message
from ...frameworks import get_adapter


class ConfiguredChatAgent(Agent):
    """Chat agent using kosmos.toml runtime.

    For LangChain, maintains a per-session chain instance (separate memory) and
    executes synchronously, returning the assistant reply text as a Message.
    """

    def __init__(self, cfg: AgentConfig) -> None:
        self.cfg = cfg
        self._instances: Dict[str, Any] = {}

    def runtime(self) -> str:
        return self.cfg.runtime

    def respond(
        self, session_id: str, user_input: str
    ) -> Tuple[List[Artifact], Message | None]:
        rt = (self.cfg.runtime or "").lower()
        adapter = get_adapter(
            rt,
            adapter_path=self.cfg.adapter
            or self.cfg.raw.get("adapter")
            or self.cfg.raw.get("adopter"),
            base_dir=self.cfg.base_dir,
        )
        if not adapter.supports_chat():
            raise NotImplementedError(
                f"Chat not implemented for runtime: {self.cfg.runtime}"
            )

        # Delegate to adapter; pass entrypoint string so adapter can manage per-session state
        from ...runtime import session_context
        from ...artifacts import artifact_tracking_context

        arts_cfg = self.cfg.raw.get("artifacts") or {}
        import os as _os

        _env_mode = _os.getenv("UAI_ARTIFACTS")
        _enabled = (
            True if (str(arts_cfg.get("tracking") or "").lower() == "auto") else False
        )
        if _env_mode is not None:
            _enabled = _env_mode.lower() == "auto"
        _inc = _os.getenv("UAI_ARTIFACTS_INCLUDE")
        _exc = _os.getenv("UAI_ARTIFACTS_EXCLUDE")
        _base = (
            _os.getenv("UAI_ARTIFACTS_BASEDIR")
            or arts_cfg.get("base_dir")
            or self.cfg.base_dir
        )
        _inc_list = [s.strip() for s in _inc.split(",") if s.strip()] if _inc else None
        _exc_list = [s.strip() for s in _exc.split(",") if s.strip()] if _exc else None

        with (
            session_context(session_id),
            artifact_tracking_context(
                bool(_enabled),
                include=_inc_list,
                exclude=_exc_list,
                base_dir=str(_base),
            ),
        ):
            text = adapter.chat_respond(
                self.cfg.entrypoint,
                session_id=session_id,
                user_input=user_input,
                state=None,
                config_dir=self.cfg.base_dir,
            )
        reply = Message(role="assistant", content=text)
        return [], reply

    def next(
        self, state: dict, user_input: str
    ) -> Tuple[dict, List[Artifact], Message | None]:
        rt = (self.cfg.runtime or "").lower()
        adapter = get_adapter(
            rt,
            adapter_path=self.cfg.adapter
            or self.cfg.raw.get("adapter")
            or self.cfg.raw.get("adopter"),
            base_dir=self.cfg.base_dir,
        )
        if not adapter.supports_chat():
            raise NotImplementedError(
                f"Chat not implemented for runtime: {self.cfg.runtime}"
            )
        # Stateless runs use a synthetic session id
        from ...runtime import session_context
        from ...artifacts import artifact_tracking_context

        arts_cfg = self.cfg.raw.get("artifacts") or {}
        import os as _os

        _env_mode = _os.getenv("UAI_ARTIFACTS")
        _enabled = (
            True if (str(arts_cfg.get("tracking") or "").lower() == "auto") else False
        )
        if _env_mode is not None:
            _enabled = _env_mode.lower() == "auto"
        _inc = _os.getenv("UAI_ARTIFACTS_INCLUDE")
        _exc = _os.getenv("UAI_ARTIFACTS_EXCLUDE")
        _base = (
            _os.getenv("UAI_ARTIFACTS_BASEDIR")
            or arts_cfg.get("base_dir")
            or self.cfg.base_dir
        )
        _inc_list = [s.strip() for s in _inc.split(",") if s.strip()] if _inc else None
        _exc_list = [s.strip() for s in _exc.split(",") if s.strip()] if _exc else None

        with (
            session_context("stateless"),
            artifact_tracking_context(
                bool(_enabled),
                include=_inc_list,
                exclude=_exc_list,
                base_dir=str(_base),
            ),
        ):
            adapter.chat_respond(
                self.cfg.entrypoint,
                session_id="stateless",
                user_input=user_input,
                state=state or {},
                config_dir=self.cfg.base_dir,
            )
        # For stateless next we don't return messages; just state/artifacts
        return state or {}, [], None
