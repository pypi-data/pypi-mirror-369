"""Agentic Interfaces

Protocol and abstract classes declaring the stable contracts used by the
controller and adapters (Planner, Verifier, Reflexion, ModelClient).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Protocol
from pydantic import BaseModel
from ..models import (
    ReasoningPlan,
    VerificationResult,
    IsaacPatchV1,
)


class ModelClient(Protocol):
    def generate_json(
        self, *, prompt: str, grammar: str | None = None, timeout: int = 30
    ) -> dict:
        ...


class Planner(ABC):
    @abstractmethod
    def plan(self, goal: str, max_steps: int = 6) -> ReasoningPlan:
        ...


class Verifier(ABC):
    @abstractmethod
    def verify_patch(self, patch: IsaacPatchV1) -> VerificationResult:
        ...


class Reflexion(ABC):
    @abstractmethod
    def improve(self, patch: IsaacPatchV1, reasons: List[str]) -> IsaacPatchV1:
        ...


class ControllerSpec(BaseModel):
    cutoff: float = 0.80
    deep_n_best: int = 3
    enable_reflexion: bool = True
