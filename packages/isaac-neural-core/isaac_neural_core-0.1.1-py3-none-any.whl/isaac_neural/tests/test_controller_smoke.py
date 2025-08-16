from isaac_neural.agentic.adapters.reasoning_adapter import JSONPlanner
from isaac_neural.agentic.adapters.verifier_adapter import ToolFirstVerifier
from isaac_neural.agentic.adapters.reflexion_adapter import SimpleReflexion
from isaac_neural.agentic.controller_executor import ControllerExecutor


class DummyClient:
    def generate_json(
        self, *, prompt: str, grammar: str | None = None, timeout: int = 30
    ) -> dict:
        return {
            "id": "plan-1",
            "steps": [
                {"id": "s1", "title": "Doc", "description": "", "task_class": "doc"}
            ],
        }


def test_controller_dry_run():
    ctrl = ControllerExecutor(
        planner=JSONPlanner(DummyClient(), system_prompt=""),
        verifier=ToolFirstVerifier(0.80),
        reflexion=SimpleReflexion(),
    )
    patch = ctrl.run(goal="add readme")
    assert patch.plan
    assert patch.diffs and patch.tests and patch.commands
