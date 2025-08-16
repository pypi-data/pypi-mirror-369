"""Prompting components for ISAAC Neural.

Exports the high-powered prompt agent wrapper that can leverage the IDE's
enhanced prompt agent when available, falling back to a simple local refiner.
"""

from .high_powered_agent import HighPowerPromptAgent, HighPowerPromptAgentConfig

__all__ = [
    "HighPowerPromptAgent",
    "HighPowerPromptAgentConfig",
]
