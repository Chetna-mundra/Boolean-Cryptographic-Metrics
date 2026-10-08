"""Truth-table generation helpers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import product

from src.utils import ensure_bit_vector

VectorBooleanFunction = Callable[[Sequence[int]], Sequence[int]]


def generate_truth_table(F: VectorBooleanFunction, n: int, m: int | None = None):
    """Return [(input_tuple, output_list), ...] over every n-bit input."""
    if n <= 0:
        raise ValueError("n must be positive")

    table = []
    for x in product([0, 1], repeat=n):
        output = list(F(x))
        if m is not None:
            output = ensure_bit_vector(output, expected_length=m)
        else:
            output = ensure_bit_vector(output)
        table.append((x, output))
    return table
