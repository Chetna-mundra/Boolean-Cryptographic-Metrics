"""Empirical avalanche analysis for vector Boolean functions."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import product

from src.dependency import flip_bit
from src.utils import ensure_bit_vector

VectorBooleanFunction = Callable[[Sequence[int]], Sequence[int]]


def avalanche_matrix(F: VectorBooleanFunction, n: int, m: int) -> list[list[float]]:
    """
    Return A where A[i][j] is the exact probability that fj changes when xi
    is flipped, under the uniform distribution over all 2^n inputs.
    """
    if n <= 0 or m <= 0:
        raise ValueError("n and m must be positive")

    counts = [[0 for _ in range(m)] for _ in range(n)]
    total_inputs = 1 << n

    for x in product([0, 1], repeat=n):
        original_output = ensure_bit_vector(F(x), expected_length=m)

        for i in range(n):
            changed_output = ensure_bit_vector(F(flip_bit(x, i)), expected_length=m)
            for j in range(m):
                if original_output[j] != changed_output[j]:
                    counts[i][j] += 1

    return [[count / total_inputs for count in row] for row in counts]


def average_avalanche_probability(A: Sequence[Sequence[float]]) -> float:
    """Return the mean entry of an avalanche matrix."""
    values = [value for row in A for value in row]
    if not values:
        raise ValueError("Avalanche matrix must be non-empty.")
    return sum(values) / len(values)
