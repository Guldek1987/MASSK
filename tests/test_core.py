import numpy as np
import pandas as pd

from src.bootstrap_ci import macro_f1, paired_bootstrap_difference
from src.evaluate import classification_metrics
from src.preprocessing import (
    duplicate_components,
    normalize_doi,
    normalize_text,
    validate_split_disjointness,
)
from src.retrieval import (
    apply_classwise_residual,
    exact_top_k,
    neighbour_class_probabilities,
)


def test_normalization_and_duplicate_components():
    frame = pd.DataFrame(
        {
            "doi": ["https://doi.org/10.1/ABC", "doi:10.1/abc", ""],
            "title": ["A <b>Title</b>", "A Title", "Different"],
            "abstract": ["Text", "Text", "Other"],
            "split": ["train", "train", "validation"],
        }
    )
    frame["duplicate_group_id"] = duplicate_components(frame)
    assert normalize_doi(frame.loc[0, "doi"]) == "10.1/abc"
    assert normalize_text(frame.loc[0, "title"]) == "A Title"
    assert frame.loc[0, "duplicate_group_id"] == frame.loc[1, "duplicate_group_id"]
    validate_split_disjointness(frame)


def test_exact_retrieval_excludes_self_and_builds_probabilities():
    view = np.eye(3, dtype=np.float32)
    scores, indices = exact_top_k(
        [view],
        [view],
        k=1,
        query_ids=np.array(["a", "b", "c"]),
        reference_ids=np.array(["a", "b", "c"]),
    )
    assert np.all(indices[:, 0] != np.arange(3))
    probabilities = neighbour_class_probabilities(
        indices, scores, np.array([0, 1, 2]), num_classes=3
    )
    np.testing.assert_allclose(probabilities.sum(axis=1), 1.0)


def test_zero_residual_is_exact_noop():
    base = np.array([[0.7, 0.2, 0.1], [0.2, 0.3, 0.5]])
    neighbour = np.array([[0.2, 0.7, 0.1], [0.6, 0.1, 0.3]])
    result = apply_classwise_residual(base, neighbour, np.zeros(3))
    np.testing.assert_allclose(result, base, atol=1e-12)


def test_metrics_and_bootstrap_are_deterministic():
    labels = np.array([0, 1, 0, 1, 0, 1])
    candidate = np.array(
        [
            [0.9, 0.1],
            [0.1, 0.9],
            [0.8, 0.2],
            [0.2, 0.8],
            [0.7, 0.3],
            [0.3, 0.7],
        ]
    )
    comparator = np.full((6, 2), 0.5)
    metrics = classification_metrics(labels, candidate)
    assert metrics["accuracy"] == 1.0
    first = paired_bootstrap_difference(
        labels, candidate, comparator, macro_f1, iterations=100, seed=7
    )
    second = paired_bootstrap_difference(
        labels, candidate, comparator, macro_f1, iterations=100, seed=7
    )
    assert first == second
