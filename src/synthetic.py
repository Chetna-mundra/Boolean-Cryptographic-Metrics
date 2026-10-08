"""Reproducible synthetic Boolean transformations for exploratory experiments."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence


def evaluate_anf_masks(x: Sequence[int], masks: Sequence[int]) -> int:
    """Evaluate an ANF represented by monomial bitmasks."""
    result = 0
    for mask in masks:
        term = 1
        for i, bit in enumerate(x):
            if mask & (1 << i):
                term &= bit
                if term == 0:
                    break
        result ^= term
    return result


def make_random_anf_transform(
    n: int,
    m: int,
    *,
    seed: int,
    p_linear: float,
    p_quadratic: float,
    p_cubic: float = 0.0,
) -> Callable:
    """
    Build a deterministic pseudo-random vector Boolean function from sparse ANFs.
    This is intended as an experimental baseline; it is not a cryptographic construction.
    """
    if n <= 0 or m <= 0:
        raise ValueError("n and m must be positive")
    for probability in (p_linear, p_quadratic, p_cubic):
        if probability < 0 or probability > 1:
            raise ValueError("term probabilities must lie in [0,1]")

    rng = random.Random(seed)
    component_masks: list[tuple[int, ...]] = []

    linear_masks = [1 << i for i in range(n)]
    quadratic_masks = [
        (1 << i) | (1 << j)
        for i in range(n)
        for j in range(i + 1, n)
    ]
    cubic_masks = [
        (1 << i) | (1 << j) | (1 << k)
        for i in range(n)
        for j in range(i + 1, n)
        for k in range(j + 1, n)
    ]

    for output_index in range(m):
        masks: list[int] = []

        for mask in linear_masks:
            if rng.random() < p_linear:
                masks.append(mask)
        for mask in quadratic_masks:
            if rng.random() < p_quadratic:
                masks.append(mask)
        for mask in cubic_masks:
            if rng.random() < p_cubic:
                masks.append(mask)

        # Guarantee that each component is nonconstant and make the family
        # reproducible even for very sparse parameter choices.
        if not masks:
            masks.append(1 << (output_index % n))

        component_masks.append(tuple(sorted(set(masks))))

    frozen = tuple(component_masks)

    def transform(x):
        return [evaluate_anf_masks(x, masks) for masks in frozen]

    return transform


def synthetic_experiment_specs(base_seed: int = 20261008):
    """Return a varied, reproducible family of 4x4 synthetic transformations."""
    profiles = [
        ("Sparse linear", 0.25, 0.00, 0.00),
        ("Dense linear", 0.70, 0.00, 0.00),
        ("Sparse quadratic", 0.30, 0.12, 0.00),
        ("Medium quadratic", 0.45, 0.28, 0.00),
        ("Mixed cubic", 0.45, 0.25, 0.12),
    ]

    specs = []
    counter = 0
    for profile_name, p1, p2, p3 in profiles:
        for replicate in range(4):
            seed = base_seed + counter
            counter += 1
            specs.append(
                (
                    f"{profile_name} {replicate + 1}",
                    make_random_anf_transform(
                        4,
                        4,
                        seed=seed,
                        p_linear=p1,
                        p_quadratic=p2,
                        p_cubic=p3,
                    ),
                    4,
                    4,
                    "synthetic",
                )
            )
    return specs
