"""Graph DTOs for solver DAG execution shared across services."""

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field
from isaac_neural.models import ReasoningStep


class GraphNode(BaseModel):
    id: UUID
    step: ReasoningStep
    deps: List[UUID] = Field(default_factory=list)


TopoBatch = List[GraphNode]
