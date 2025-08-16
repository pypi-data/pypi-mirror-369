"""Thin Controller Executor (Legacy Compatibility)

Minimal orchestration wrapper that uses provided Planner/Verifier/Reflexion
implementations. Retained for backward compatibility while the new
`isaac_neural/controller/executor.py` provides advanced routing and escalation.
"""

from __future__ import annotations
from pydantic import BaseModel
from ..models import IsaacPatchV1, ReasoningPlan
from ..models.isaac_patch_v1 import Diff, TestCmd, Command
from .interfaces import Planner, Verifier, Reflexion, ControllerSpec
from ..telemetry import start_span


class ControllerExecutor(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True,
    }
    planner: Planner
    verifier: Verifier
    reflexion: Reflexion | None = None
    spec: ControllerSpec = ControllerSpec()

    def run(self, goal: str) -> IsaacPatchV1:
        with start_span("isaac.controller.plan", {"goal": goal}):
            plan: ReasoningPlan = self.planner.plan(goal=goal)

        # For now, ask planner for a single patch via tool-first JSON prompt
        patch = IsaacPatchV1(
            plan=f"Execute {len(plan.steps)} steps",
            diffs=[Diff(file="README.md", unified_diff="+placeholder")],
            tests=[TestCmd(command="echo run-tests", cwd=".")],
            risks=["low"],
            commands=[Command(cmd="echo", args=["ok"], paths=["."])],
        )

        with start_span("isaac.verifier.run", {"stage": "pre"}):
            result = self.verifier.verify_patch(patch)
        if not result.passed and self.reflexion and self.spec.enable_reflexion:
            with start_span(
                "isaac.reflexion.run", {"reasons_count": len(result.reasons)}
            ):
                patch = self.reflexion.improve(patch, result.reasons)

        # final gate
        with start_span("isaac.verifier.run", {"stage": "final"}):
            final = self.verifier.verify_patch(patch)
        if not final.passed:
            raise RuntimeError(f"verification failed: score={final.score}")
        return patch
