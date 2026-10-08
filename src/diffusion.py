"""Structural diffusion metrics."""

from __future__ import annotations

from collections.abc import Sequence


def _validate_matrix(D: Sequence[Sequence[int]]) -> tuple[int, int]:
    if not D or not D[0]:
        raise ValueError("Dependency matrix must be non-empty.")

    m = len(D[0])
    if any(len(row) != m for row in D):
        raise ValueError("Dependency matrix rows must have equal length.")
    if any(value not in (0, 1) for row in D for value in row):
        raise ValueError("Dependency matrix must contain only 0 and 1.")

    return len(D), m


def per_input_diffusion(D: Sequence[Sequence[int]]) -> list[int]:
    _validate_matrix(D)
    return [sum(row) for row in D]


def diffusion_score(D: Sequence[Sequence[int]]) -> int:
    """Diffusion degree d(F) = min_i d_i."""
    return min(per_input_diffusion(D))


def dependency_density(D: Sequence[Sequence[int]]) -> float:
    """Fraction of possible input-output dependencies that are present."""
    n, m = _validate_matrix(D)
    return sum(sum(row) for row in D) / (n * m)


def normalized_diffusion(D: Sequence[Sequence[int]]) -> float:
    """Normalize d(F) to [0,1] by dividing by the number of outputs."""
    _, m = _validate_matrix(D)
    return diffusion_score(D) / m
