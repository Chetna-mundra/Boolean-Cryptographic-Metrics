"""Generate ShannonDiff figures and exploratory correlation summaries."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
SUMMARY_FILE = RESULTS_DIR / "summary.csv"
DEPENDENCY_DIR = RESULTS_DIR / "dependency_matrices"
AVALANCHE_DIR = RESULTS_DIR / "avalanche_matrices"
PLOTS_DIR = RESULTS_DIR / "plots"

NUMERIC_FIELDS = {
    "n": int,
    "m": int,
    "anf_degree": int,
    "degree_normalized": float,
    "diffusion": float,
    "diffusion_normalized": float,
    "dependency_density": float,
    "confusion": float,
    "confusion_normalized": float,
    "average_avalanche": float,
    "sac_error": float,
    "sac_max_error": float,
    "sac_score": float,
}


def read_summary() -> list[dict[str, object]]:
    if not SUMMARY_FILE.exists():
        raise FileNotFoundError(
            f"{SUMMARY_FILE} does not exist. Run 'python run_experiments.py' first."
        )

    results: list[dict[str, object]] = []
    with SUMMARY_FILE.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            parsed: dict[str, object] = dict(row)
            for field, converter in NUMERIC_FIELDS.items():
                parsed[field] = converter(row[field])
            results.append(parsed)
    return results


def read_matrix(path: Path) -> list[list[float]]:
    with path.open("r", encoding="utf-8") as handle:
        matrix = [[float(value) for value in row] for row in csv.reader(handle)]
    if not matrix or not matrix[0]:
        raise ValueError(f"Matrix file is empty: {path}")
    return matrix


def plot_heatmap(
    matrix: list[list[float]],
    *,
    title: str,
    save_path: Path,
    value_format: str,
) -> None:
    rows, columns = len(matrix), len(matrix[0])
    fig, ax = plt.subplots(figsize=(max(5.5, columns * 0.75), max(4.5, rows * 0.65)))
    image = ax.imshow(matrix, aspect="auto", vmin=0.0, vmax=1.0)
    fig.colorbar(image, ax=ax)

    ax.set_xticks(range(columns), labels=[f"f{j}" for j in range(columns)])
    ax.set_yticks(range(rows), labels=[f"x{i}" for i in range(rows)])
    ax.set_xlabel("Output component")
    ax.set_ylabel("Input bit")
    ax.set_title(title)

    for i in range(rows):
        for j in range(columns):
            ax.text(j, i, format(matrix[i][j], value_format), ha="center", va="center")

    fig.tight_layout()
    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def create_heatmaps(results: list[dict[str, object]]) -> None:
    for result in results:
        experiment_id = str(result["id"])
        name = str(result["name"])

        D = read_matrix(DEPENDENCY_DIR / f"{experiment_id}.csv")
        A = read_matrix(AVALANCHE_DIR / f"{experiment_id}.csv")

        plot_heatmap(
            D,
            title=f"{name}: dependency matrix",
            save_path=PLOTS_DIR / f"{experiment_id}_dependency_heatmap.png",
            value_format=".0f",
        )
        plot_heatmap(
            A,
            title=f"{name}: avalanche matrix",
            save_path=PLOTS_DIR / f"{experiment_id}_avalanche_heatmap.png",
            value_format=".2f",
        )


def create_bar_plot(
    results: list[dict[str, object]],
    *,
    key: str,
    ylabel: str,
    title: str,
    filename: str,
) -> None:
    names = [str(result["name"]) for result in results]
    values = [float(result[key]) for result in results]

    fig, ax = plt.subplots(figsize=(max(10, len(results) * 1.05), 6))
    bars = ax.bar(names, values)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=35)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    fig.tight_layout()
    fig.savefig(PLOTS_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def create_core_comparison_plots(results: list[dict[str, object]]) -> None:
    """Readable bar charts for the named toy + cryptographic transformations."""
    core = [result for result in results if result["category"] != "synthetic"]

    create_bar_plot(
        core,
        key="degree_normalized",
        ylabel="Algebraic degree / n",
        title="Normalized algebraic degree",
        filename="comparison_degree_normalized.png",
    )
    create_bar_plot(
        core,
        key="diffusion_normalized",
        ylabel="d(F) / m",
        title="Normalized structural diffusion",
        filename="comparison_diffusion_normalized.png",
    )
    create_bar_plot(
        core,
        key="confusion_normalized",
        ylabel="c(F) / n",
        title="Normalized structural confusion",
        filename="comparison_confusion_normalized.png",
    )
    create_bar_plot(
        core,
        key="sac_score",
        ylabel="Project normalized SAC score",
        title="SAC summary score",
        filename="comparison_sac_score.png",
    )
    create_bar_plot(
        core,
        key="sac_max_error",
        ylabel="Maximum |A[i,j] - 0.5|",
        title="Worst SAC deviation",
        filename="comparison_sac_max_error.png",
    )


def create_scatter_plot(
    results: list[dict[str, object]],
    *,
    x_key: str,
    x_label: str,
    filename: str,
) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 6.5))

    categories = sorted({str(result["category"]) for result in results})
    for category in categories:
        subset = [result for result in results if result["category"] == category]
        ax.scatter(
            [float(result[x_key]) for result in subset],
            [float(result["sac_score"]) for result in subset],
            label=category,
            s=55,
        )

    # Label only the named non-synthetic cases; labeling every generated point is unreadable.
    for result in results:
        if result["category"] == "synthetic":
            continue
        ax.annotate(
            str(result["name"]),
            (float(result[x_key]), float(result["sac_score"])),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )

    ax.set_xlabel(x_label)
    ax.set_ylabel("Project normalized SAC score")
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.03, 1.03)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def average_ranks(values: list[float]) -> list[float]:
    """Return 1-based average ranks with correct handling of ties."""
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    position = 0

    while position < len(order):
        end = position + 1
        while end < len(order) and values[order[end]] == values[order[position]]:
            end += 1
        average_rank = ((position + 1) + end) / 2.0
        for k in range(position, end):
            ranks[order[k]] = average_rank
        position = end

    return ranks


def pearson_correlation(x: list[float], y: list[float]) -> float:
    """Pearson r; NaN is returned when either variable has zero variance."""
    if len(x) != len(y) or len(x) < 2:
        return math.nan

    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    dx = [value - mean_x for value in x]
    dy = [value - mean_y for value in y]
    denominator = math.sqrt(sum(value * value for value in dx) * sum(value * value for value in dy))

    if denominator == 0:
        return math.nan
    return sum(a * b for a, b in zip(dx, dy)) / denominator


def spearman_correlation(x: list[float], y: list[float]) -> float:
    """Spearman rho computed as Pearson correlation of average ranks."""
    if len(x) != len(y) or len(x) < 2:
        return math.nan
    return pearson_correlation(average_ranks(x), average_ranks(y))


def correlation_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    metrics = [
        ("Normalized algebraic degree", "degree_normalized"),
        ("Normalized diffusion", "diffusion_normalized"),
        ("Dependency density", "dependency_density"),
        ("Normalized confusion", "confusion_normalized"),
    ]

    rows = []
    y = [float(result["sac_score"]) for result in results]
    for label, key in metrics:
        x = [float(result[key]) for result in results]
        rows.append(
            {
                "metric": label,
                "n": len(results),
                "pearson_r": pearson_correlation(x, y),
                "spearman_rho": spearman_correlation(x, y),
            }
        )
    return rows


def save_correlations(rows: list[dict[str, object]]) -> None:
    path = RESULTS_DIR / "correlations.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "n", "pearson_r", "spearman_rho"])
        writer.writeheader()
        writer.writerows(rows)

    print("\nExploratory correlations with the project SAC score:")
    for row in rows:
        pearson = float(row["pearson_r"])
        spearman = float(row["spearman_rho"])
        p_text = "undefined" if math.isnan(pearson) else f"{pearson:.3f}"
        s_text = "undefined" if math.isnan(spearman) else f"{spearman:.3f}"
        print(f"  {row['metric']:<30} Pearson={p_text:>9}  Spearman={s_text:>9}")


def create_relationship_plots(results: list[dict[str, object]]) -> None:
    create_scatter_plot(
        results,
        x_key="degree_normalized",
        x_label="Normalized algebraic degree (degree / n)",
        filename="degree_vs_sac.png",
    )
    create_scatter_plot(
        results,
        x_key="diffusion_normalized",
        x_label="Normalized diffusion (d(F) / m)",
        filename="diffusion_vs_sac.png",
    )
    create_scatter_plot(
        results,
        x_key="confusion_normalized",
        x_label="Normalized confusion (c(F) / n)",
        filename="confusion_vs_sac.png",
    )
    create_scatter_plot(
        results,
        x_key="dependency_density",
        x_label="Dependency density",
        filename="dependency_density_vs_sac.png",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-heatmaps",
        action="store_true",
        help="Skip per-function dependency and avalanche heatmaps.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    results = read_summary()

    if not args.skip_heatmaps:
        print("Creating dependency and avalanche heatmaps...")
        create_heatmaps(results)

    print("Creating comparison plots...")
    create_core_comparison_plots(results)

    print("Creating structural-vs-SAC plots...")
    create_relationship_plots(results)

    rows = correlation_rows(results)
    save_correlations(rows)
    print(f"\nPlots saved to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
