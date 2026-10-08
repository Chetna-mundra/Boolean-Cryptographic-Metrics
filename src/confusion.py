"""Paper-defined structural confusion analysis."""

from __future__ import annotations
from collections.abc import Callable, Sequence
from src.anf import output_component, variable_support

VectorBooleanFunction = Callable[[Sequence[int]], Sequence[int]]


def confusion_sets(F: VectorBooleanFunction, n: int, m: int) -> list[set[int]]:
    """Return Omega^j, the ANF variable-support set of each output component."""
    if n <= 0 or m <= 0:
        raise ValueError("n and m must be positive")

    return [variable_support(output_component(F, j), n) for j in range(m)]


def confusion_variables(F: VectorBooleanFunction, n: int, m: int) -> set[int]:
    """Return the intersection of all component support sets."""
    omega_sets = confusion_sets(F, n, m)
    if not omega_sets:
        return set()

    common = omega_sets[0].copy()
    for omega in omega_sets[1:]:
        common &= omega
    return common


def confusion_score(F: VectorBooleanFunction, n: int, m: int) -> int:
    """Paper-defined confusion degree c(F) = cardinality of the support intersection."""
    return len(confusion_variables(F, n, m))


def normalized_confusion(F: VectorBooleanFunction, n: int, m: int) -> float:
    """Normalize c(F) to [0,1] by dividing by the number of inputs."""
    return confusion_score(F, n, m) / n
