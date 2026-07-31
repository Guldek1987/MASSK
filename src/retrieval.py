"""Exact dual-view retrieval and the MASSK class-wise residual."""

from __future__ import annotations

import numpy as np


def l2_normalize(values: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    return values / np.maximum(norms, epsilon)


def exact_top_k(
    query_views: list[np.ndarray],
    reference_views: list[np.ndarray],
    k: int,
    query_ids: np.ndarray | None = None,
    reference_ids: np.ndarray | None = None,
    chunk_size: int = 1024,
) -> tuple[np.ndarray, np.ndarray]:
    """Return exact mean-cosine top-k scores and reference indices."""
    if not query_views or len(query_views) != len(reference_views):
        raise ValueError("Query and reference views must be non-empty and aligned")
    if any(len(view) != len(query_views[0]) for view in query_views):
        raise ValueError("All query views must contain the same number of rows")
    if any(len(view) != len(reference_views[0]) for view in reference_views):
        raise ValueError("All reference views must contain the same number of rows")
    if k < 1 or k > len(reference_views[0]):
        raise ValueError("k must be between 1 and the number of reference rows")

    q_views = [l2_normalize(view) for view in query_views]
    r_views = [l2_normalize(view) for view in reference_views]
    all_scores: list[np.ndarray] = []
    all_indices: list[np.ndarray] = []

    for start in range(0, len(q_views[0]), chunk_size):
        stop = min(start + chunk_size, len(q_views[0]))
        similarity = sum(
            query[start:stop] @ reference.T
            for query, reference in zip(q_views, r_views, strict=True)
        ) / len(q_views)

        if query_ids is not None and reference_ids is not None:
            same_record = query_ids[start:stop, None] == reference_ids[None, :]
            similarity[same_record] = -np.inf

        candidate_indices = np.argpartition(similarity, -k, axis=1)[:, -k:]
        candidate_scores = np.take_along_axis(similarity, candidate_indices, axis=1)
        order = np.argsort(candidate_scores, axis=1)[:, ::-1]
        all_indices.append(np.take_along_axis(candidate_indices, order, axis=1))
        all_scores.append(np.take_along_axis(candidate_scores, order, axis=1))

    return np.vstack(all_scores), np.vstack(all_indices)


def softmax_weights(scores: np.ndarray, temperature: float = 0.07) -> np.ndarray:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    scaled = np.asarray(scores, dtype=np.float64) / temperature
    scaled -= scaled.max(axis=1, keepdims=True)
    weights = np.exp(scaled)
    return weights / weights.sum(axis=1, keepdims=True)


def neighbour_class_probabilities(
    neighbour_indices: np.ndarray,
    neighbour_scores: np.ndarray,
    reference_labels: np.ndarray,
    num_classes: int,
    temperature: float = 0.07,
) -> np.ndarray:
    """Convert nearest-neighbour evidence into a class distribution."""
    labels = np.asarray(reference_labels, dtype=np.int64)[neighbour_indices]
    weights = softmax_weights(neighbour_scores, temperature=temperature)
    probabilities = np.zeros((len(labels), num_classes), dtype=np.float64)
    for class_id in range(num_classes):
        probabilities[:, class_id] = (weights * (labels == class_id)).sum(axis=1)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    return probabilities


def apply_classwise_residual(
    base_probabilities: np.ndarray,
    neighbour_probabilities: np.ndarray,
    coefficients: np.ndarray,
    probability_floor: float = 1e-7,
) -> np.ndarray:
    """Apply the uncertainty-scaled class-wise log-probability residual.

    z_c = log(p_base,c) + (1 - max(p_base)) * gamma_c *
          (log(p_neighbour,c) - log(p_base,c))
    """
    base = np.clip(np.asarray(base_probabilities, dtype=np.float64), probability_floor, 1)
    neighbour = np.clip(
        np.asarray(neighbour_probabilities, dtype=np.float64), probability_floor, 1
    )
    gamma = np.asarray(coefficients, dtype=np.float64)
    if base.shape != neighbour.shape:
        raise ValueError("Base and neighbour probabilities must have identical shapes")
    if gamma.shape != (base.shape[1],):
        raise ValueError("One coefficient is required per class")

    uncertainty = (1.0 - base.max(axis=1, keepdims=True))
    logits = np.log(base) + uncertainty * gamma[None, :] * (
        np.log(neighbour) - np.log(base)
    )
    logits -= logits.max(axis=1, keepdims=True)
    probabilities = np.exp(logits)
    return probabilities / probabilities.sum(axis=1, keepdims=True)
