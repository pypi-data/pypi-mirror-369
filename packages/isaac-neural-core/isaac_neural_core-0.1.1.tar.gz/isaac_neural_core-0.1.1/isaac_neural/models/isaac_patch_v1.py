from __future__ import annotations
"""Strict Patch Contract – IsaacPatchV1

This schema defines the deterministic patch output enforced across lanes and
providers. Downstream systems rely on this contract to apply changes and run
verifier gates safely.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Diff(BaseModel):
    file: str
    unified_diff: str


class TestCmd(BaseModel):
    command: str
    cwd: str = "."


class Command(BaseModel):
    cmd: str
    args: List[str] = []
    paths: List[str] = []


class IsaacPatchV1(BaseModel):
    """Strict patch contract enforced across lanes and providers."""

    plan: str = Field(min_length=1)
    diffs: List[Diff]
    tests: List[TestCmd]
    risks: List[str]
    commands: List[Command]
    citations: Optional[List[str]] = None