"""Deterministic paired bootstrap confidence intervals for model differences."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, log_loss

MetricFunction = Callable[[np.ndarray, np.ndarray], float]


def macro_f1(labels: np.ndarray, probabilities: np.ndarray) -> float:
    return float(f1_score(labels, probabilities.argmax(axis=1), average="macro"))


def accuracy(labels: np.ndarray, probabilities: np.ndarray) -> float:
    return float(accuracy_score(labels, probabilities.argmax(axis=1)))


def nll(labels: np.ndarray, probabilities: np.ndarray) -> float:
    return float(log_loss(labels, probabilities, labels=np.arange(probabilities.shape[1])))


def brier(labels: np.ndarray, probabilities: np.ndarray) -> float:
    one_hot = np.eye(probabilities.shape[1])[labels]
    return float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1)))


METRICS: dict[str, MetricFunction] = {
    "accuracy": accuracy,
    "macro_f1": macro_f1,
    "nll": nll,
    "brier_multiclass": brier,
}


def paired_bootstrap_difference(
    labels: np.ndarray,
    candidate_probabilities: np.ndarray,
    comparator_probabilities: np.ndarray,
    metric: MetricFunction,
    iterations: int = 2000,
    confidence_level: float = 0.95,
    seed: int = 20260731,
    clusters: np.ndarray | None = None,
) -> dict[str, float | int]:
    """Estimate candidate-minus-comparator intervals with paired resampling."""
    labels = np.asarray(labels, dtype=np.int64)
    candidate = np.asarray(candidate_probabilities, dtype=np.float64)
    comparator = np.asarray(comparator_probabilities, dtype=np.float64)
    if candidate.shape != comparator.shape or len(labels) != len(candidate):
        raise ValueError("Labels and both prediction matrices must align")

    rng = np.random.default_rng(seed)
    point = metric(labels, candidate) - metric(labels, comparator)
    bootstrap_values = np.empty(iterations, dtype=np.float64)

    if clusters is None:
        for iteration in range(iterations):
            index = rng.integers(0, len(labels), size=len(labels))
            bootstrap_values[iteration] = metric(labels[index], candidate[index]) - metric(
                labels[index], comparator[index]
            )
        resampling_units = len(labels)
    else:
        clusters = np.asarray(clusters)
        if len(clusters) != len(labels):
            raise ValueError("clusters must align with labels")
        unique_clusters = np.unique(clusters)
        members = {cluster: np.flatnonzero(clusters == cluster) for cluster in unique_clusters}
        for iteration in range(iterations):
            sampled_clusters = rng.choice(unique_clusters, size=len(unique_clusters), replace=True)
            index = np.concatenate([members[cluster] for cluster in sampled_clusters])
            bootstrap_values[iteration] = metric(labels[index], candidate[index]) - metric(
                labels[index], comparator[index]
            )
        resampling_units = len(unique_clusters)

    alpha = 1.0 - confidence_level
    lower, upper = np.quantile(bootstrap_values, [alpha / 2, 1 - alpha / 2])
    return {
        "delta": float(point),
        "ci_lower": float(lower),
        "ci_upper": float(upper),
        "confidence_level": confidence_level,
        "iterations": iterations,
        "resampling_units": resampling_units,
        "seed": seed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metric", choices=sorted(METRICS), default="macro_f1")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--candidate-prefix", default="massk_prob_")
    parser.add_argument("--comparator-prefix", default="prism_prob_")
    parser.add_argument("--cluster-column")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--confidence-level", type=float, default=0.95)
    parser.add_argument("--seed", type=int, default=20260731)
    args = parser.parse_args()

    frame = pd.read_csv(args.predictions)
    candidate_columns = sorted(
        column for column in frame.columns if column.startswith(args.candidate_prefix)
    )
    comparator_columns = sorted(
        column for column in frame.columns if column.startswith(args.comparator_prefix)
    )
    if not candidate_columns or len(candidate_columns) != len(comparator_columns):
        raise KeyError("Candidate and comparator probability columns must be present and aligned")

    result = paired_bootstrap_difference(
        frame[args.label_column].to_numpy(),
        frame[candidate_columns].to_numpy(),
        frame[comparator_columns].to_numpy(),
        METRICS[args.metric],
        iterations=args.iterations,
        confidence_level=args.confidence_level,
        seed=args.seed,
        clusters=(
            frame[args.cluster_column].to_numpy() if args.cluster_column else None
        ),
    )
    result["metric"] = args.metric
    result["contrast"] = "candidate_minus_comparator"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([result]).to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
