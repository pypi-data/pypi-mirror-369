"""Routing Configuration and Decisions

Defines lane configs, routing tables, and the `route_for` helper used to map
task classes to lanes/models and n-best counts.
"""

from __future__ import annotations

from typing import Dict
from pydantic import BaseModel, Field


class LaneConfig(BaseModel):
    name: str
    max_tokens: int
    timeout_seconds: int
    n_best: int
    model: str


class RoutingTable(BaseModel):
    defaults: Dict[str, str] = Field(
        default_factory=lambda: {"lane": "std", "model": "llama_strong"}
    )
    by_class: Dict[str, Dict[str, str]] = Field(default_factory=dict)


class RouterConfig(BaseModel):
    lanes: Dict[str, LaneConfig]
    routing: RoutingTable


DEFAULT_CONFIG = RouterConfig(
    lanes={
        "quick": LaneConfig(
            name="quick", max_tokens=512, timeout_seconds=8, n_best=1, model="oss_fast"
        ),
        "std": LaneConfig(
            name="std", max_tokens=1536, timeout_seconds=20, n_best=1, model="oss_fast"
        ),
        "deep": LaneConfig(
            name="deep",
            max_tokens=4096,
            timeout_seconds=60,
            n_best=3,
            model="llama_strong",
        ),
    },
    routing=RoutingTable(
        defaults={"lane": "std", "model": "llama_strong"},
        by_class={
            "doc": {"lane": "quick", "model": "oss_fast"},
            "test": {"lane": "std", "model": "oss_fast"},
            "small_fix": {"lane": "std", "model": "oss_fast"},
            "refactor": {"lane": "deep", "model": "llama_strong"},
            "plan": {"lane": "deep", "model": "llama_strong"},
            "migrate": {"lane": "deep", "model": "llama_strong"},
        },
    ),
)


class RouteDecision(BaseModel):
    lane: str
    model: str
    n_best: int


def route_for(task_class: str, config: RouterConfig | None = None) -> RouteDecision:
    cfg = config or DEFAULT_CONFIG
    mapping = cfg.routing.by_class.get(task_class)
    if mapping is None:
        lane_name = cfg.routing.defaults.get("lane", "std")
        model_name = cfg.routing.defaults.get("model", cfg.lanes[lane_name].model)
    else:
        lane_name = mapping.get("lane", cfg.routing.defaults.get("lane", "std"))
        model_name = mapping.get("model", cfg.lanes[lane_name].model)

    lane = cfg.lanes.get(lane_name, cfg.lanes["std"])
    return RouteDecision(lane=lane.name, model=model_name, n_best=lane.n_best)
