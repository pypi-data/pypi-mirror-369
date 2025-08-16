"""Planner Adapter – JSON Mode

Asks a model client to emit a `ReasoningPlan` as JSON. Grammar enforcement is
recommended at the model gateway. This adapter keeps the interface minimal.
"""

from __future__ import annotations
from ...models import ReasoningPlan, ReasoningStep
from ..interfaces import Planner, ModelClient
from ...prompting import HighPowerPromptAgent, HighPowerPromptAgentConfig


class JSONPlanner(Planner):
    """Planner that asks a model to emit ReasoningPlan in JSON (grammar optional)."""

    def __init__(self, client: ModelClient, system_prompt: str):
        self.client = client
        self.system_prompt = system_prompt
        # Hybrid prompt agent: leverage IDE enhanced agent when available
        self._prompt_agent = HighPowerPromptAgent(
            HighPowerPromptAgentConfig(),
            model_client=client,
        )

    def plan(self, goal: str, max_steps: int = 6) -> ReasoningPlan:
        # Refine the user goal via high-powered prompt agent (hybrid)
        refined = self._prompt_agent.refine(goal)
        refined_goal = refined.get("refined_prompt", goal)
        prompt = (
            f"You are a planner. Split the goal into <= {max_steps} steps.\n"
            "Return JSON with {id,title,description,task_class}."
        )
        data = self.client.generate_json(
            prompt=prompt.replace("the goal", refined_goal)
        )
        steps = [ReasoningStep(**s) for s in data.get("steps", [])]
        return ReasoningPlan(id=data.get("id", "plan-1"), goal=goal, steps=steps)
