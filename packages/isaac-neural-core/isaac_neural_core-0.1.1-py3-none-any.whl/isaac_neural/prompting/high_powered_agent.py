"""High-Powered Prompt Agent Adapter

Bridges ISAAC Neural to the IDE's enhanced prompt agent. If the IDE agent is
importable, it will be used; otherwise this falls back to a minimal local
refiner/validator to keep flows working.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import inspect
import asyncio
from pydantic import BaseModel, Field


class HighPowerPromptAgentConfig(BaseModel):
    target_agent: str = Field(default="general")
    max_context_snippets: int = 8
    context_relevance_threshold: float = 0.4


class HighPowerPromptAgent:
    def __init__(
        self,
        cfg: HighPowerPromptAgentConfig,
        model_client: Any,
        indexing_client: Any | None = None,
    ) -> None:
        self.cfg = cfg
        self.model_client = model_client
        self.indexing_client = indexing_client
        self._delegate = self._try_build_delegate()

    def _try_build_delegate(self) -> Optional[Any]:
        """Try to import and build the IDE enhanced prompt agent; return None."""
        try:
            from isaac_agents.agents.enhanced_prompt_agent_pkg import (
                build_enhanced_prompt_agent,
                EnhancedPromptAgentConfig,
            )

            ide_cfg = EnhancedPromptAgentConfig(
                max_context_snippets=self.cfg.max_context_snippets,
                context_relevance_threshold=self.cfg.context_relevance_threshold,
            )
            return build_enhanced_prompt_agent(
                ide_cfg, self.model_client, self.indexing_client
            )
        except Exception:
            return None

    def refine(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Refine and validate a prompt using the best available implementation.

        This method is synchronous for easy embedding. If the IDE agent exposes
        async methods, we will attempt to run them via `asyncio.run`. When
        running inside an existing event loop, we fall back to a no-op refine to
        avoid loop conflicts.
        """

        def _maybe_await(val: Any) -> Optional[Dict[str, Any]]:
            if inspect.isawaitable(val):
                try:
                    result = asyncio.run(val)
                except RuntimeError:
                    # Event loop already running; cannot await safely here
                    # Best-effort: close coroutine to avoid "never awaited" warnings
                    try:
                        close = getattr(val, "close", None)
                        if callable(close):
                            close()  # type: ignore[func-returns-value]
                    except Exception:
                        pass
                    return None
            else:
                result = val
            return result if isinstance(result, dict) else None

        if self._delegate is not None:
            # Try process_request with various call shapes
            pr = getattr(self._delegate, "process_request", None)
            if callable(pr):
                for args, kwargs in (
                    ((user_input,), {}),
                    ((), {"user_input": user_input}),
                    ((), {"text": user_input}),
                ):
                    try:
                        maybe = _maybe_await(pr(*args, **kwargs))  # type: ignore
                        if maybe and "refined_prompt" in maybe:
                            return maybe
                    except Exception:
                        continue

            # Try run with common call shapes
            rn = getattr(self._delegate, "run", None)
            if callable(rn):
                for args, kwargs in (
                    ((user_input, self.cfg.target_agent, self.cfg, context or {}), {}),
                    (
                        (),
                        {
                            "user_input": user_input,
                            "target_agent": self.cfg.target_agent,
                            "cfg": self.cfg,
                            "context": context or {},
                        },
                    ),
                ):
                    try:
                        maybe = _maybe_await(rn(*args, **kwargs))  # type: ignore
                        if maybe and "refined_prompt" in maybe:
                            return maybe
                    except Exception:
                        continue

        # Fallback minimal refiner: echo + trivial validation
        refined = user_input.strip()
        return {
            "refined_prompt": refined,
            "validation": {"ok": True, "reasons": []},
            "snippets": [],
        }
