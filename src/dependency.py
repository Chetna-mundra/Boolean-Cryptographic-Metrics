"""Structural input-output dependency analysis."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import product

from src.utils import ensure_bit_vector

VectorBooleanFunction = Callable[[Sequence[int]], Sequence[int]]


def flip_bit(x: Sequence[int], i: int) -> tuple[int, ...]:
    """Return x with bit i flipped."""
    values = ensure_bit_vector(x)
    if i < 0 or i >= len(values):
        raise IndexError("bit index out of range")

    values[i] ^= 1
    return tuple(values)


def dependency_matrix(F: VectorBooleanFunction, n: int, m: int) -> list[list[int]]:
    """Compute D where D[i][j] = 1 iff input xi can affect output fj."""
    if n <= 0 or m <= 0:
        raise ValueError("n and m must be positive")

    D = [[0 for _ in range(m)] for _ in range(n)]

    for x in product([0, 1], repeat=n):
        original_output = ensure_bit_vector(F(x), expected_length=m)

        for i in range(n):
            changed_input = flip_bit(x, i)
            changed_output = ensure_bit_vector(F(changed_input), expected_length=m)

            for j in range(m):
                if original_output[j] != changed_output[j]:
                    D[i][j] = 1

    return D
