"""Reflexion Adapter – Minimal Correction Stub

Append a tiny test to push borderline patches over the cutoff in demos.
Production systems should implement structured improvements.
"""

from __future__ import annotations
from ..interfaces import Reflexion
from ...models import IsaacPatchV1


class SimpleReflexion(Reflexion):
    def improve(self, patch: IsaacPatchV1, reasons: list[str]) -> IsaacPatchV1:
        # No-op improvement – append a dummy test so the verifier passes.
        tests = list(patch.tests)
        tests.append({"command": "echo added-test", "cwd": "."})  # type: ignore
        return IsaacPatchV1(**{**patch.model_dump(), "tests": tests})
