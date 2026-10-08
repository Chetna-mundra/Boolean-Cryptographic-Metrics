"""Algebraic Normal Form (ANF) analysis for Boolean transformations."""

from __future__ import annotations
from collections.abc import Callable, Sequence
from src.utils import ensure_bit_vector

BooleanFunction = Callable[[Sequence[int]], int]
VectorBooleanFunction = Callable[[Sequence[int]], Sequence[int]]


def truth_values(f: BooleanFunction, n: int) -> list[int]:
    """Evaluate a Boolean function on all inputs in LSB-first mask order."""
    if n < 0:
        raise ValueError("n must be non-negative")

    values: list[int] = []

    for mask in range(1 << n):
        x = [(mask >> i) & 1 for i in range(n)]
        value = f(x)
        if value not in (0, 1):
            raise ValueError("Boolean component functions must return 0 or 1.")
        values.append(int(value))

    return values


def output_component(F: VectorBooleanFunction, j: int) -> BooleanFunction:
    """Return the j-th scalar Boolean component of a vector Boolean function."""
    if j < 0:
        raise ValueError("j must be non-negative")

    def component(x: Sequence[int]) -> int:
        output = list(F(x))
        if j >= len(output):
            raise ValueError(f"Output component {j} does not exist.")
        return int(output[j])

    return component


def mobius_transform(values: Sequence[int], n: int) -> list[int]:
    """Convert a truth table into ANF coefficients over F_2."""
    expected = 1 << n
    if len(values) != expected:
        raise ValueError(f"Expected {expected} truth values, received {len(values)}.")
    if any(value not in (0, 1) for value in values):
        raise ValueError("Truth values must contain only 0 and 1.")

    coefficients = list(values)

    for i in range(n):
        for mask in range(1 << n):
            if mask & (1 << i):
                coefficients[mask] ^= coefficients[mask ^ (1 << i)]

    return coefficients


def anf_coefficients(f: BooleanFunction, n: int) -> list[int]:
    """Return the ANF coefficient vector of f."""
    return mobius_transform(truth_values(f, n), n)


def mask_to_monomial(mask: int, n: int) -> str:
    """Convert a monomial mask to a readable product such asmask = 6 = [0,1,1](lsb first) = x1*x2."""
    if mask < 0 or mask >= (1 << n):
        raise ValueError("mask is outside the range for n variables")

    variables = [f"x{i}" for i in range(n) if mask & (1 << i)]
    return "1" if not variables else "*".join(variables)


def anf_expression(f: BooleanFunction, n: int) -> str:
    """Return a readable ANF expression for f."""
    coefficients = anf_coefficients(f, n)
    terms = [mask_to_monomial(mask, n) for mask, coefficient in enumerate(coefficients) if coefficient == 1]
    return "0" if not terms else " + ".join(terms)


def algebraic_degree(f: BooleanFunction, n: int) -> int:
    """Return the algebraic degree of f."""
    coefficients = anf_coefficients(f, n)
    return max(
        (mask.bit_count() for mask, coefficient in enumerate(coefficients) if coefficient),
        default=0,
    )


def variable_support(f: BooleanFunction, n: int) -> set[int]:
    """Return variables that occur in at least one nonzero ANF monomial."""
    coefficients = anf_coefficients(f, n)
    support: set[int] = set()

    for mask, coefficient in enumerate(coefficients):
        if coefficient == 0:
            continue
        for i in range(n):
            if mask & (1 << i):
                support.add(i)

    return support


def analyze_anf(F: VectorBooleanFunction, n: int, m: int) -> list[dict[str, object]]:
    """Return ANF expression, degree, and support for each output component."""
    if m <= 0:
        raise ValueError("m must be positive")

    # Validate one output shape early.
    ensure_bit_vector(F([0] * n), expected_length=m)

    results: list[dict[str, object]] = []

    for j in range(m):
        f = output_component(F, j)
        results.append(
            {
                "output": j,
                "anf": anf_expression(f, n),
                "degree": algebraic_degree(f, n),
                "support": sorted(variable_support(f, n)),
            }
        )

    return results
