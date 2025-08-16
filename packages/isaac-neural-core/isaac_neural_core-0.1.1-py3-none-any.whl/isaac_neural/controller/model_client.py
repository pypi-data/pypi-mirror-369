"""Model Client – HTTP JSON generation.

Provides a minimal HTTP client that requests JSON-only outputs from
configured model endpoints (open models, strong models, premium).

This module documents the expected endpoint contract and fields so callers
can swap providers via config without changing code.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from pydantic import BaseModel
import httpx


class ModelEndpoint(BaseModel):
    """Configuration for a model endpoint.

    Example sources are open-source HTTP gateways or premium providers.
    """

    name: str
    base_url: str
    model_id: str
    provider: Optional[str] = None


class HTTPModelClient(BaseModel):
    """Minimal HTTP client to request JSON outputs from a model gateway.

    Expected server route: POST {base_url}/api/v1/generate_json
    Required body keys: prompt, model
    Optional: grammar, max_tokens, extra params (provider-specific)
    """

    endpoint: ModelEndpoint

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def generate_json(
        self,
        *,
        prompt: str,
        grammar: str | None = None,
        timeout: int = 30,
        max_tokens: int | None = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Generate JSON from the configured model endpoint.

        Uses response_format=json_object (or grammar) on the server side.
        Callers should treat invalid JSON as retriable (once) before escalation.
        """
        url = self.endpoint.base_url.rstrip("/") + "/api/v1/generate_json"
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "model": self.endpoint.model_id,
        }
        if grammar is not None:
            payload["grammar"] = grammar
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if extra:
            payload.update(extra)

        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict):
                return data
            # If the server returns {content: {...}}
            return data.get("content", {}) if isinstance(data, dict) else {}
