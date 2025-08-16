"""Reflexion DTOs usable across services (chatbot and IDE)."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class FailureCategory(str, Enum):
    EXECUTION_ERROR = "execution_error"
    VERIFICATION_FAILURE = "verification_failure"
    QUALITY_GATE_FAILURE = "quality_gate_failure"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"
    CONFIGURATION_ERROR = "configuration_error"
    LOGIC_ERROR = "logic_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"


class RetryStrategy(str, Enum):
    IMMEDIATE = "immediate"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    MODIFIED_APPROACH = "modified_approach"
    ALTERNATIVE_TOOLS = "alternative_tools"
    SIMPLIFIED_APPROACH = "simplified_approach"
    SKIP_AND_CONTINUE = "skip_and_continue"
    ABORT_PLAN = "abort_plan"


class LearningType(str, Enum):
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    TOOL_EFFECTIVENESS = "tool_effectiveness"
    STRATEGY_REFINEMENT = "strategy_refinement"
    CONTEXT_ADAPTATION = "context_adaptation"


class FailureAnalysis(BaseModel):
    failure_id: UUID = Field(default_factory=uuid4)
    step_id: UUID
    category: FailureCategory
    root_cause: str
    contributing_factors: List[str] = Field(default_factory=list)
    error_patterns: List[str] = Field(default_factory=list)
    step_type: str
    tools_used: List[str] = Field(default_factory=list)
    execution_context: Dict[str, Any] = Field(default_factory=dict)
    severity: str
    recovery_difficulty: str
    downstream_impact: List[str] = Field(default_factory=list)
    recommended_strategy: RetryStrategy
    strategy_rationale: str
    modifications: List[str] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analyzer: str = "modular_reflexion"


class ReflexionResult(BaseModel):
    analysis_id: UUID = Field(default_factory=uuid4)
    plan_id: UUID
    failure_analyses: List[FailureAnalysis] = Field(default_factory=list)
    success_factors: List[str] = Field(default_factory=list)
    improvement_opportunities: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
    pattern_insights: List[str] = Field(default_factory=list)
    strategy_recommendations: List[str] = Field(default_factory=list)
    plan_modifications: List[str] = Field(default_factory=list)
    retry_steps: List[UUID] = Field(default_factory=list)
    alternative_approaches: List[str] = Field(default_factory=list)
    confidence_score: float = 0.5
    learning_value: float = 0.0
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_time: float = 0.0


class LearningInsight(BaseModel):
    insight_id: UUID = Field(default_factory=uuid4)
    learning_type: LearningType
    title: str
    description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    pattern: str
    frequency: int = 1
    confidence: float = 0.5
    recommendations: List[str] = Field(default_factory=list)
    impact_areas: List[str] = Field(default_factory=list)
    validated: bool = False
    validation_results: Optional[Dict[str, Any]] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    source: str


class RetryAdvice(BaseModel):
    step_id: UUID
    strategy: str
    rationale: str
    modifications: List[str] = Field(default_factory=list)
    max_attempts: int
    backoff_factor: float
    timeout_multiplier: float
