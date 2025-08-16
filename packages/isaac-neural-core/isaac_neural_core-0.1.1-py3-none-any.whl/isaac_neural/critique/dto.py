"""Critique DTOs shared by chatbot and IDE integrations."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Dimension(str, Enum):
    CORRECTNESS = "correctness"
    COMPLETENESS = "completeness"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    MAINTAINABILITY = "maintainability"
    SECURITY = "security"
    PERFORMANCE = "performance"
    ADHERENCE = "adherence"


class Severity(str, Enum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class Issue(BaseModel):
    issue_id: str
    dimension: Dimension
    severity: Severity
    title: str
    description: str
    suggestion: str
    location: Optional[str] = None
    rule_reference: Optional[str] = None


class Result(BaseModel):
    step_id: str
    overall_score: float
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    issues: List[Issue] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    meets_standards: bool
    constitutional_compliance: bool
    verification_alignment: float
    critique_model: str
    critique_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
