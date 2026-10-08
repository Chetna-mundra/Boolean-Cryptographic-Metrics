"""Shared utility helpers used across ShannonDiff."""

from __future__ import annotations

from collections.abc import Sequence


def ensure_bit_vector(bits: Sequence[int], expected_length: int | None = None) -> list[int]:
    """Validate and return a bit vector as a list of 0/1 integers."""
    values = list(bits)

    if expected_length is not None and len(values) != expected_length:
        raise ValueError(
            f"Expected {expected_length} bits, received {len(values)}."
        )

    if any(bit not in (0, 1) for bit in values):
        raise ValueError("Bit vectors must contain only 0 and 1.")

    return values


def bits_to_int_lsb(bits: Sequence[int]) -> int:
    """Convert LSB-first bits [x0, x1, ...] to an integer. Ex - [0,1,1] = 6"""
    values = ensure_bit_vector(bits)
    result = 0
    for i, bit in enumerate(values):
        result |= bit << i
    return result


def int_to_bits_lsb(value: int, width: int) -> list[int]:
    """Convert an integer to an LSB-first bit vector of the given width."""
    if width <= 0:
        raise ValueError("width must be positive")
    if value < 0 or value >= (1 << width):
        raise ValueError(f"value must lie in [0, {1 << width})")

    return [(value >> i) & 1 for i in range(width)]
