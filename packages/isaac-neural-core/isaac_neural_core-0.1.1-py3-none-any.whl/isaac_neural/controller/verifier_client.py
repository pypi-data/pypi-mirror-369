"""Tool-first Verifier Runner

Loads tool commands from a YAML config and runs them with timeouts. Produces
`VerificationResult` with pass/fail, score, and reasons suitable for gating
patch acceptance and deep-lane consensus.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel

from ..models import IsaacPatchV1, VerificationResult
from .tool_runner import run_command


class ToolVerifierRunner(BaseModel):
    """Run tool-first verification using commands from verifier.yaml.

    Config discovery:
      - VERIFIER_CONFIG env var if set
      - otherwise defaults to isaac_neural/resources/config/verifier.yaml
    """

    cutoff: float = 0.80
    config_path: str | None = None

    def _load_config(self) -> Dict:
        path = (
            Path(self.config_path)
            if self.config_path
            else Path("isaac_neural/resources/config/verifier.yaml")
        )
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def run(self, patch: IsaacPatchV1) -> VerificationResult:
        cfg = self._load_config()
        tools: Dict[str, Dict[str, object]] = cfg.get(
            "tools", {}
        )  # type: ignore[assignment]
        reasons: List[str] = []
        passed_all = True

        for name, spec in tools.items():
            command = str(spec.get("command", ""))
            timeout = int(spec.get("timeout_seconds", 30))
            if not command:
                continue
            exit_code, out, err = run_command(["bash", "-lc", command], timeout=timeout)
            if exit_code != 0:
                passed_all = False
                reasons.append(f"{name} failed: {err.strip() or out.strip()}")

        score = 0.9 if (passed_all and patch.diffs and patch.tests) else 0.6
        return VerificationResult(
            passed=score >= self.cutoff, score=score, reasons=reasons
        )
