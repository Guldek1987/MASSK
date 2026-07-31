"""Classification, calibration, and selective-risk evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    log_loss,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)


def multiclass_brier_score(labels: np.ndarray, probabilities: np.ndarray) -> float:
    one_hot = np.eye(probabilities.shape[1], dtype=np.float64)[labels]
    return float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1)))


def expected_calibration_error(
    labels: np.ndarray, probabilities: np.ndarray, bins: int = 15
) -> float:
    predictions = probabilities.argmax(axis=1)
    confidence = probabilities.max(axis=1)
    correct = predictions == labels
    edges = np.linspace(0, 1, bins + 1)
    value = 0.0
    for lower, upper in zip(edges[:-1], edges[1:], strict=True):
        mask = (confidence > lower) & (confidence <= upper)
        if mask.any():
            value += mask.mean() * abs(confidence[mask].mean() - correct[mask].mean())
    return float(value)


def area_under_risk_coverage(labels: np.ndarray, probabilities: np.ndarray) -> float:
    predictions = probabilities.argmax(axis=1)
    errors = (predictions != labels).astype(np.float64)
    ordered_probabilities = np.sort(probabilities, axis=1)
    uncertainty = 1.0 - (
        ordered_probabilities[:, -1] - ordered_probabilities[:, -2]
    )
    order = np.argsort(uncertainty, kind="stable")
    cumulative_risk = np.cumsum(errors[order]) / np.arange(1, len(errors) + 1)
    return float(np.mean(cumulative_risk))


def classification_metrics(
    labels: np.ndarray, probabilities: np.ndarray
) -> dict[str, float]:
    labels = np.asarray(labels, dtype=np.int64)
    probabilities = np.asarray(probabilities, dtype=np.float64)
    if probabilities.ndim != 2 or len(labels) != len(probabilities):
        raise ValueError("labels and probabilities must align")
    if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-6):
        raise ValueError("Each probability row must sum to one")

    predictions = probabilities.argmax(axis=1)
    errors = (predictions != labels).astype(np.int64)
    ordered_probabilities = np.sort(probabilities, axis=1)
    uncertainty = 1.0 - (
        ordered_probabilities[:, -1] - ordered_probabilities[:, -2]
    )
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(labels, predictions)),
        "macro_f1": float(f1_score(labels, predictions, average="macro")),
        "weighted_f1": float(f1_score(labels, predictions, average="weighted")),
        "macro_precision": float(
            precision_score(labels, predictions, average="macro", zero_division=0)
        ),
        "macro_recall": float(recall_score(labels, predictions, average="macro")),
        "mcc": float(matthews_corrcoef(labels, predictions)),
        "nll": float(log_loss(labels, probabilities, labels=np.arange(probabilities.shape[1]))),
        "brier_multiclass": multiclass_brier_score(labels, probabilities),
        "ece_15": expected_calibration_error(labels, probabilities, bins=15),
        "error_auroc": (
            float(roc_auc_score(errors, uncertainty))
            if np.unique(errors).size == 2
            else float("nan")
        ),
        "aurc": area_under_risk_coverage(labels, probabilities),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--probability-prefix", default="prob_")
    args = parser.parse_args()

    frame = pd.read_csv(args.predictions)
    probability_columns = sorted(
        column for column in frame.columns if column.startswith(args.probability_prefix)
    )
    if not probability_columns:
        raise KeyError(f"No probability columns start with {args.probability_prefix!r}")
    metrics = classification_metrics(
        frame[args.label_column].to_numpy(),
        frame[probability_columns].to_numpy(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix.lower() == ".json":
        args.output.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    else:
        pd.DataFrame([metrics]).to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
