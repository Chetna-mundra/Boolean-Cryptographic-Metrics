"""Strict Avalanche Criterion (SAC) summary metrics."""

from __future__ import annotations

from collections.abc import Sequence


def _values(A: Sequence[Sequence[float]]) -> list[float]:
    values = [float(value) for row in A for value in row]
    if not values:
        raise ValueError("Avalanche matrix must be non-empty.")
    if any(value < 0 or value > 1 for value in values):
        raise ValueError("Avalanche probabilities must lie in [0,1].")
    return values


def sac_error(A: Sequence[Sequence[float]]) -> float:
    """Mean absolute deviation of avalanche probabilities from the SAC target 0.5."""
    values = _values(A)
    return sum(abs(value - 0.5) for value in values) / len(values)


def sac_max_error(A: Sequence[Sequence[float]]) -> float:
    """Worst absolute deviation from the SAC target 0.5."""
    return max(abs(value - 0.5) for value in _values(A))


def sac_score(A: Sequence[Sequence[float]]) -> float:
    """normalized SAC summary score in [0,1].
       score = 1 - 2 * mean_absolute_deviation_from_0.5
    """
    return 1.0 - 2.0 * sac_error(A)
