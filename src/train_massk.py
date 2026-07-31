"""Fit the eight class-wise MASSK retrieval-residual coefficients."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yaml

try:
    from .retrieval import apply_classwise_residual
except ImportError:
    from retrieval import apply_classwise_residual


def class_balanced_weights(labels: np.ndarray, num_classes: int) -> torch.Tensor:
    import torch

    counts = np.bincount(labels, minlength=num_classes).astype(np.float64)
    if np.any(counts == 0):
        raise ValueError("Every class must occur in the fitting data")
    weights = len(labels) / (num_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)


def fit_classwise_coefficients(
    base_probabilities: np.ndarray,
    neighbour_probabilities: np.ndarray,
    labels: np.ndarray,
    learning_rate: float = 0.05,
    weight_decay: float = 0.0,
    l2_penalty: float = 0.01,
    max_epochs: int = 600,
    patience: int = 60,
    seed: int = 20260731,
    device: str | None = None,
) -> tuple[np.ndarray, dict[str, float | int]]:
    """Fit bounded coefficients using class-balanced cross-entropy."""
    import torch
    import torch.nn.functional as functional

    base = np.clip(np.asarray(base_probabilities, dtype=np.float32), 1e-7, 1)
    neighbour = np.clip(np.asarray(neighbour_probabilities, dtype=np.float32), 1e-7, 1)
    target = np.asarray(labels, dtype=np.int64)
    if base.shape != neighbour.shape or len(base) != len(target):
        raise ValueError("Probability matrices and labels must align")

    torch.manual_seed(seed)
    selected_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    base_tensor = torch.tensor(base, device=selected_device)
    neighbour_tensor = torch.tensor(neighbour, device=selected_device)
    target_tensor = torch.tensor(target, device=selected_device)
    weights = class_balanced_weights(target, base.shape[1]).to(selected_device)
    raw_coefficients = torch.zeros(base.shape[1], device=selected_device, requires_grad=True)
    optimizer = torch.optim.AdamW(
        [raw_coefficients], lr=learning_rate, weight_decay=weight_decay
    )

    best_loss = float("inf")
    best_coefficients: np.ndarray | None = None
    wait = 0
    epochs_run = 0
    for epoch in range(max_epochs):
        optimizer.zero_grad(set_to_none=True)
        coefficients = torch.sigmoid(raw_coefficients)
        uncertainty = 1.0 - base_tensor.max(dim=1, keepdim=True).values
        logits = torch.log(base_tensor) + uncertainty * coefficients[None, :] * (
            torch.log(neighbour_tensor) - torch.log(base_tensor)
        )
        loss = functional.cross_entropy(logits, target_tensor, weight=weights)
        loss = loss + l2_penalty * coefficients.square().mean()
        loss.backward()
        optimizer.step()
        epochs_run = epoch + 1

        current_loss = float(loss.detach().cpu())
        if current_loss < best_loss - 1e-9:
            best_loss = current_loss
            best_coefficients = coefficients.detach().cpu().numpy().copy()
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                break

    if best_coefficients is None:
        raise RuntimeError("Coefficient fitting did not produce a finite solution")
    return best_coefficients, {
        "best_objective": best_loss,
        "epochs_run": epochs_run,
        "seed": seed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="NPZ with base_probabilities, neighbour_probabilities, labels, and optional train_mask",
    )
    parser.add_argument("--config", type=Path, default=Path("configs/massk.yaml"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--predictions-output", type=Path)
    parser.add_argument("--device")
    args = parser.parse_args()

    arrays = np.load(args.input)
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    base = arrays["base_probabilities"]
    neighbour = arrays["neighbour_probabilities"]
    labels = arrays["labels"]
    mask = arrays["train_mask"].astype(bool) if "train_mask" in arrays else np.ones(len(labels), bool)

    coefficients, diagnostics = fit_classwise_coefficients(
        base[mask],
        neighbour[mask],
        labels[mask],
        l2_penalty=float(config["residual"]["l2_penalty"]),
        seed=int(config["project"]["random_seed"]),
        device=args.device,
    )
    payload = {
        "coefficients": coefficients.tolist(),
        "classes": config["classes"],
        "diagnostics": diagnostics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.predictions_output:
        probabilities = apply_classwise_residual(base, neighbour, coefficients)
        np.savez_compressed(
            args.predictions_output,
            probabilities=probabilities,
            predictions=probabilities.argmax(axis=1),
            labels=labels,
        )


if __name__ == "__main__":
    main()
