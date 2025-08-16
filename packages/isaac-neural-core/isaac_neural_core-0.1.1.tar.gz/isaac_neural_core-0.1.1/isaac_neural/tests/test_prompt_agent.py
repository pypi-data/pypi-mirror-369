from isaac_neural.prompting import HighPowerPromptAgent, HighPowerPromptAgentConfig


def test_high_power_prompt_agent_fallback_refines_safely():
    agent = HighPowerPromptAgent(HighPowerPromptAgentConfig(), model_client=None)
    out = agent.refine("  improve foo  ")
    assert "refined_prompt" in out
    assert out["refined_prompt"] == "improve foo"
    assert out["validation"]["ok"] is True
