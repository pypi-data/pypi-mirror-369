"""Merge/Selection Utilities

Helpers for selecting the best candidate patch based on verifier results.
"""

from __future__ import annotations

from typing import List
from ..models import IsaacPatchV1, VerificationResult


def select_best_patch(
    candidates: List[tuple[IsaacPatchV1, VerificationResult]]
) -> IsaacPatchV1:
    """Select the best patch by score; first that passes cutoff preferred.

    Expects (patch, result) tuples where result.score∈[0,1].
    """
    passing = [p for p, r in candidates if r.passed]
    if passing:
        # pick highest score among passing
        return max(
            passing, key=lambda p: next(r.score for (pp, r) in candidates if pp is p)
        )
    # otherwise highest score overall
    return max(
        (p for p, _ in candidates),
        key=lambda p: next(r.score for (pp, r) in candidates if pp is p),
    )
