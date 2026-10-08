"""Run ShannonDiff experiments and export reproducible numerical results."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from src.anf import analyze_anf
from src.avalanche import avalanche_matrix, average_avalanche_probability
from src.boolean_functions import (
    cubic_mix,
    identity_function,
    linear_mix,
    quadratic_mix,
    sample_function,
    uneven_nonlinear,
)
from src.confusion import confusion_score, confusion_variables
from src.dependency import dependency_matrix
from src.diffusion import dependency_density, diffusion_score
from src.sac import sac_error, sac_max_error, sac_score
from src.sboxes import aes_sbox, present_sbox
from src.synthetic import synthetic_experiment_specs

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
DEPENDENCY_DIR = RESULTS_DIR / "dependency_matrices"
AVALANCHE_DIR = RESULTS_DIR / "avalanche_matrices"
ANF_DIR = RESULTS_DIR / "anf"


@dataclass(frozen=True)
class Experiment:
    name: str
    function: Callable
    n: int
    m: int
    category: str


def slugify(name: str) -> str:
    """Create a stable filesystem-safe experiment identifier."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "experiment"


def build_experiments(include_synthetic: bool = True, seed: int = 20261008) -> list[Experiment]:
    """Build the complete reproducible experiment set."""
    experiments = [
        Experiment("Identity", identity_function, 3, 3, "toy"),
        Experiment("Linear Mix", linear_mix, 3, 3, "toy"),
        Experiment("Sample Function", sample_function, 3, 3, "toy"),
        Experiment("Quadratic Mix", quadratic_mix, 3, 3, "toy"),
        Experiment("Uneven Nonlinear", uneven_nonlinear, 3, 3, "toy"),
        Experiment("Cubic Mix", cubic_mix, 3, 3, "toy"),
        Experiment("PRESENT S-box", present_sbox, 4, 4, "cryptographic"),
        Experiment("AES S-box", aes_sbox, 8, 8, "cryptographic"),
    ]

    if include_synthetic:
        experiments.extend(
            Experiment(name, function, n, m, category)
            for name, function, n, m, category in synthetic_experiment_specs(seed)
        )

    ids = [slugify(experiment.name) for experiment in experiments]
    if len(ids) != len(set(ids)):
        raise ValueError("Experiment names produce duplicate filesystem identifiers.")

    return experiments


def prepare_result_directories(clean: bool) -> None:
    if clean and RESULTS_DIR.exists():
        shutil.rmtree(RESULTS_DIR)

    for directory in (RESULTS_DIR, DEPENDENCY_DIR, AVALANCHE_DIR, ANF_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def save_matrix(matrix, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(matrix)


def save_anf(anf_results: list[dict[str, object]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["output", "degree", "support", "anf"])
        writer.writeheader()
        for item in anf_results:
            writer.writerow(
                {
                    "output": item["output"],
                    "degree": item["degree"],
                    "support": " ".join(f"x{i}" for i in item["support"]),
                    "anf": item["anf"],
                }
            )


def analyze_function(experiment: Experiment, verbose: bool = False) -> dict[str, object]:
    """Compute all structural and empirical metrics for one transformation."""
    name, F, n, m = experiment.name, experiment.function, experiment.n, experiment.m
    experiment_id = slugify(name)

    anf_results = analyze_anf(F, n, m)
    anf_degree = max(int(item["degree"]) for item in anf_results)

    D = dependency_matrix(F, n, m)
    diffusion = diffusion_score(D)
    density = dependency_density(D)

    common_variables = confusion_variables(F, n, m)
    confusion = confusion_score(F, n, m)

    A = avalanche_matrix(F, n, m)
    avg_avalanche = average_avalanche_probability(A)
    mean_sac_error = sac_error(A)
    worst_sac_error = sac_max_error(A)
    normalized_sac_score = sac_score(A)

    save_matrix(D, DEPENDENCY_DIR / f"{experiment_id}.csv")
    save_matrix(A, AVALANCHE_DIR / f"{experiment_id}.csv")
    save_anf(anf_results, ANF_DIR / f"{experiment_id}.csv")

    if verbose:
        print("\n" + "=" * 72)
        print(f"{name}  [{experiment.category}]  F_2^{n} -> F_2^{m}")
        print("=" * 72)
        for item in anf_results:
            print(f"f{item['output']} = {item['anf']}   degree={item['degree']}")
        print("Dependency matrix:")
        for row in D:
            print(row)
        print("Avalanche matrix:")
        for row in A:
            print([round(value, 4) for value in row])

    return {
        "id": experiment_id,
        "name": name,
        "category": experiment.category,
        "n": n,
        "m": m,
        "anf_degree": anf_degree,
        "degree_normalized": anf_degree / n,
        "diffusion": diffusion,
        "diffusion_normalized": diffusion / m,
        "dependency_density": density,
        "confusion": confusion,
        "confusion_normalized": confusion / n,
        "confusion_variables": " ".join(f"x{i}" for i in sorted(common_variables)),
        "average_avalanche": avg_avalanche,
        "sac_error": mean_sac_error,
        "sac_max_error": worst_sac_error,
        "sac_score": normalized_sac_score,
    }


def save_summary(results: list[dict[str, object]]) -> Path:
    path = RESULTS_DIR / "summary.csv"
    if not results:
        raise ValueError("No experiment results to save.")

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    return path


def print_summary(results: list[dict[str, object]]) -> None:
    header = (
        f"{'Function':<25}{'Cat.':<15}{'n':>3}{'deg/n':>9}{'d/m':>9}"
        f"{'c/n':>9}{'SAC':>9}{'max err':>10}"
    )
    print("\n" + header)
    print("-" * len(header))
    for result in results:
        print(
            f"{str(result['name']):<25}{str(result['category']):<15}{int(result['n']):>3}"
            f"{float(result['degree_normalized']):>9.3f}"
            f"{float(result['diffusion_normalized']):>9.3f}"
            f"{float(result['confusion_normalized']):>9.3f}"
            f"{float(result['sac_score']):>9.3f}"
            f"{float(result['sac_max_error']):>10.3f}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-synthetic",
        action="store_true",
        help="Run only the hand-designed and cryptographic transformations.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20261008,
        help="Base seed for the reproducible synthetic ANF family.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full ANFs and matrices. AES output is long.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not remove the previous results directory before running.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prepare_result_directories(clean=not args.no_clean)

    experiments = build_experiments(
        include_synthetic=not args.no_synthetic,
        seed=args.seed,
    )

    results = [analyze_function(experiment, verbose=args.verbose) for experiment in experiments]
    summary_path = save_summary(results)
    print_summary(results)
    print(f"\nSaved {len(results)} experiments to {summary_path}")


if __name__ == "__main__":
    main()
