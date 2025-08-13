# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project adheres to Semantic Versioning.

## [0.1.1] - 2025-08-12

- Add LangChain runtime adapter with chain support (invoke/run) and output normalization.
- Add session-based chat support; split `respond(session)` and `next(state)` APIs.
- Unify adapter interface for both Run and Chat via `RuntimeAdapter`.
- Support custom adapters via `agent.adapter = "module:attr"`; enforce explicit inheritance from `RuntimeAdapter`.
- Wire custom adapters for both run and chat; add example `examples/custom_adapter` and integration test.
- Add GitHub Actions CI for tests, Ruff, mypy (via pre-commit) and PyPI publish workflow.
- Fix Ruff issues and tidy imports/examples; minor README updates.
- CLI: add `uai run cancel` and `uai run stop` to cancel runs.
- API: allow adding artifacts to runs (`POST /run/{id}/artifacts`) and chat sessions (`POST /chat/{session}/artifacts`).
- Utils: expose `post_log`, `add_run_artifact`, `add_chat_artifact`, and `request_human_input` to let user code manage logs/artifacts and input waiting.

## [0.1.0] - 2025-08-10

- Initial release with FastAPI service, run queue (inline/Procrastinate), and CrewAI + callable runtimes.
- Examples for callable, CrewAI, and human-in-the-loop CrewAI.

[0.1.1]: https://github.com/your-org/unified-agent-interface/releases/tag/0.1.1
[0.1.0]: https://github.com/your-org/unified-agent-interface/releases/tag/0.1.0
