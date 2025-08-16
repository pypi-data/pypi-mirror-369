from __future__ import annotations
"""Reasoning/Planning Schemas

Stable Pydantic models for planning and verification records used across
planner, controller, and IDE safeguard.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class VerificationLevel(str, Enum):
    CODE = "code"
    INFRA = "infrastructure"
    POLICY = "policy"
    DOCS = "docs"


class QualityGate(BaseModel):
    level: VerificationLevel
    required: bool = True
    timeout_seconds: int = 60
    name: str


class StepExecutionResult(BaseModel):
    step_id: str
    ok: bool
    output: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)


class ReasoningStep(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    task_class: str = Field(description="doc|small_fix|test|refactor|plan|migrate")


class ReasoningPlan(BaseModel):
    id: str
    goal: str
    steps: List[ReasoningStep]


class PlanningContext(BaseModel):
    repo_root: str
    env: Dict[str, str] = Field(default_factory=dict)


class DecisionRecord(BaseModel):
    step_id: str
    decision: str
    score: float
    reasons: List[str] = Field(default_factory=list)


class PlanningMemory(BaseModel):
    # lightweight store for Reflexion learnings
    items: List[DecisionRecord] = Field(default_factory=list)