"""Verifier Adapter – Heuristic (Stub)

This adapter is a placeholder. Prefer `controller/verifier_client.py` which
executes real tools. Keep this for unit tests and simple demos.
"""

from __future__ import annotations
from ..interfaces import Verifier
from ...models import IsaacPatchV1, VerificationResult


class ToolFirstVerifier(Verifier):
    """Stub verifier – replace with real tool invocations (lint/type/tests)."""

    def __init__(self, cutoff: float = 0.80):
        self.cutoff = cutoff

    def verify_patch(self, patch: IsaacPatchV1) -> VerificationResult:
        # Minimal heuristic: non-empty diffs/tests -> high score
        base = 0.9 if patch.diffs and patch.tests else 0.6
        return VerificationResult(passed=base >= self.cutoff, score=base, reasons=[])
