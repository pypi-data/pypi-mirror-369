"""Agentic Controller Executor

Coordinates planning, routing, generation (n-best for deep), verification,
optional reflexion, and premium escalation.

Sections in this module are clearly marked to improve readability and
operational debugging.
"""

from __future__ import annotations
import os
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

from pydantic import BaseModel, ValidationError

from ..models import IsaacPatchV1, ReasoningPlan
from ..agentic.interfaces import Planner, Verifier, Reflexion
from ..agentic.adapters.reasoning_adapter import JSONPlanner
from ..telemetry import start_span
from .routing import route_for
from .model_client import HTTPModelClient, ModelEndpoint


class AgenticController(BaseModel):
    """High-level controller coordinating routing, generation, and verification.

    Responsibilities:
    - Plan steps using a low-cost model
    - Route by task class to select lane/model and n-best
    - Generate strict IsaacPatchV1 JSON (retry-on-invalid once)
    - Verify via tools; reflexion once if allowed; escalate to premium as needed

    Attributes:
        planner: Planner implementation used to generate a ReasoningPlan
        verifier: Verifier implementation used for tool-first gating
        reflexion: Optional Reflexion implementation for one correction pass
        cutoff: Score threshold used to decide pass/fail and escalation
    """

    planner: Planner
    verifier: Verifier
    reflexion: Reflexion | None = None
    cutoff: float = 0.80

    model_config = {
        "arbitrary_types_allowed": True,
    }

    def run(self, goal: str) -> IsaacPatchV1:
        """Execute the full controller pipeline for a given goal.

        Args:
            goal: Developer goal or task description to accomplish.

        Returns:
            IsaacPatchV1: A strict, tool-first patch ready for downstream apply.

        Raises:
            RuntimeError: If verification fails even after escalation and reflexion.
        """
        # ============================================
        # Section: Load Config & Prompts
        # ============================================
        # Load configs and prompts
        agentic_cfg_path = os.environ.get(
            "AGENTIC_CONFIG", "isaac_neural/resources/config/agentic.yaml"
        )
        router_cfg_path = os.environ.get(
            "ROUTER_CONFIG", "isaac_neural/resources/config/router.yaml"
        )
        planner_prompt_path = os.environ.get(
            "PLANNER_SYSTEM_PROMPT", "isaac_neural/resources/prompts/planner.system.txt"
        )

        with open(agentic_cfg_path, "r", encoding="utf-8") as fh:
            agentic_cfg: Dict = yaml.safe_load(fh) or {}

        def _expand_env(obj):
            if isinstance(obj, str):
                return os.path.expandvars(obj)
            if isinstance(obj, dict):
                return {k: _expand_env(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_expand_env(v) for v in obj]
            return obj

        with open(router_cfg_path, "r", encoding="utf-8") as fh:
            router_cfg_raw: Dict = _expand_env(yaml.safe_load(fh) or {})
        with open(planner_prompt_path, "r", encoding="utf-8") as fh:
            planner_system_prompt = fh.read()

        cutoff = float(agentic_cfg.get("cutoff", self.cutoff))
        escalation_cfg = (
            agentic_cfg.get("escalation", {})
            if isinstance(agentic_cfg.get("escalation"), dict)
            else {}
        )
        escalation_enabled = bool(escalation_cfg.get("enabled", True))

        # ============================================
        # Section: Build Model Endpoints & Clients
        # ============================================
        # Build endpoints/clients from router models
        models_section: Dict[str, Dict[str, str]] = router_cfg_raw.get("models", {})
        endpoints: Dict[str, ModelEndpoint] = {}
        for name, m in models_section.items():
            endpoints[name] = ModelEndpoint(
                name=name,
                base_url=m.get("base_url", ""),
                model_id=m.get("model_id", m.get("provider", "")),
                provider=m.get("provider"),
            )
        clients: Dict[str, HTTPModelClient] = {
            k: HTTPModelClient(endpoint=v) for k, v in endpoints.items()
        }

        # ============================================
        # Section: Planning (cheap route)
        # ============================================
        # Plan using cheap oss_fast
        oss_client = clients.get("oss_fast")
        assert oss_client is not None, "oss_fast model not configured"
        planner_impl: Planner = JSONPlanner(client=oss_client, system_prompt="")

        with start_span("isaac.controller.plan", {"goal": goal}):
            plan: ReasoningPlan = planner_impl.plan(
                goal=goal,
                max_steps=int(agentic_cfg.get("max_steps", 6)),
            )

        # ============================================
        # Section: Routing (lane/model/n_best)
        # ============================================
        # Decide route (deep if any deep-class step)
        needs_deep = any(route_for(s.task_class).lane == "deep" for s in plan.steps)
        decision = route_for(
            "refactor"
            if needs_deep
            else (plan.steps[0].task_class if plan.steps else "plan")
        )
        lane = decision.lane
        model_name = decision.model
        n_best = decision.n_best

        # ============================================
        # Section: Generation (n-best for deep) with single retry-on-invalid
        # ============================================
        # Generate patches (n-best for deep lane)
        gen_client = clients.get(model_name)
        assert gen_client is not None, f"model {model_name} not configured"

        def generate_candidate() -> IsaacPatchV1:
            prompt = f"{planner_system_prompt}\nGoal: {goal}\nSteps: {len(plan.steps)}"
            try:
                data = gen_client.generate_json(prompt=prompt, max_tokens=None)
                return IsaacPatchV1(**data)
            except ValidationError:
                # Retry once with smaller output budget hint
                data = gen_client.generate_json(
                    prompt=prompt + "\nReturn minimal JSON.",
                    max_tokens=512,
                )
                return IsaacPatchV1(**data)

        candidates: List[Tuple[IsaacPatchV1, float, List[str]]] = []
        if lane == "deep" and n_best > 1:
            with ThreadPoolExecutor(max_workers=n_best) as pool:
                futures = [pool.submit(generate_candidate) for _ in range(n_best)]
                for fut in as_completed(futures):
                    patch = fut.result()
                    with start_span("isaac.verifier.run", {"stage": "pre"}):
                        result = self.verifier.verify_patch(patch)
                    candidates.append((patch, result.score, result.reasons))
            # Select best by score (and pass if possible)
            best_patch = max(candidates, key=lambda t: t[1])[0]
            patch = best_patch
        else:
            patch = generate_candidate()

        # ============================================
        # Section: Verify → Reflex → Verify
        # ============================================
        # Verify and optionally reflex
        with start_span("isaac.verifier.run", {"stage": "final"}):
            final = self.verifier.verify_patch(patch)
        if not final.passed and self.reflexion:
            with start_span(
                "isaac.reflexion.run", {"reasons_count": len(final.reasons)}
            ):
                patch = self.reflexion.improve(patch, final.reasons)
            with start_span("isaac.verifier.run", {"stage": "final_post_reflex"}):
                final = self.verifier.verify_patch(patch)

        # ============================================
        # Section: Premium Escalation (conditional)
        # ============================================
        # Escalate to premium if still below cutoff or high-risk class present
        high_risk = set(agentic_cfg.get("high_risk_classes", []))
        risk_present = any(s.task_class in high_risk for s in plan.steps)
        if (
            escalation_enabled
            and (not final.passed or final.score < cutoff or risk_present)
            and "premium" in clients
        ):
            premium_client = clients["premium"]

            def generate_premium() -> IsaacPatchV1:
                prompt = (
                    f"{planner_system_prompt}\n[Premium]\nGoal: {goal}\n"
                    f"Steps: {len(plan.steps)}"
                )
                data = premium_client.generate_json(
                    prompt=prompt,
                    max_tokens=None,
                )
                return IsaacPatchV1(**data)

            with start_span("isaac.gen.call", {"lane": lane, "model_id": "premium"}):
                patch = generate_premium()
            with start_span("isaac.verifier.run", {"stage": "final_premium"}):
                final = self.verifier.verify_patch(patch)

        if not final.passed:
            raise RuntimeError(f"verification failed: score={final.score}")
        return patch
