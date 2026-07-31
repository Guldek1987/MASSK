"""Deterministic text normalization, identifier cleaning, and deduplication."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import unicodedata
from pathlib import Path

import pandas as pd

HTML_TAG_RE = re.compile(r"<[^>]+>")
LATEX_COMMAND_RE = re.compile(r"\\(?:[a-zA-Z]+|.)")
WHITESPACE_RE = re.compile(r"\s+")
DOI_PREFIX_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.I)


def normalize_text(value: object) -> str:
    """Normalize text without changing word order or inventing content."""
    if value is None or pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKC", html.unescape(str(value)))
    text = HTML_TAG_RE.sub(" ", text)
    text = LATEX_COMMAND_RE.sub(" ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def normalize_title(value: object) -> str:
    """Return a case-folded title suitable for exact duplicate checks."""
    text = normalize_text(value).casefold()
    text = re.sub(r"[^\w\s]", " ", text)
    return WHITESPACE_RE.sub(" ", text).strip()


def normalize_doi(value: object) -> str:
    """Normalize DOI URLs and DOI-prefixed values to the bare DOI."""
    if value is None or pd.isna(value):
        return ""
    doi = DOI_PREFIX_RE.sub("", str(value).strip()).strip().lower()
    return doi.rstrip(" .;,")


def text_sha256(value: object) -> str:
    """Hash normalized text for reproducible exact-content matching."""
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


class UnionFind:
    """Small union-find implementation used to create duplicate components."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if self.rank[root_left] < self.rank[root_right]:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left
        if self.rank[root_left] == self.rank[root_right]:
            self.rank[root_left] += 1


def duplicate_components(
    frame: pd.DataFrame,
    doi_column: str = "doi",
    title_column: str = "title",
    abstract_column: str = "abstract",
) -> pd.Series:
    """Build transitive exact-duplicate groups from DOI, title, and abstract."""
    union_find = UnionFind(len(frame))
    first_seen: dict[tuple[str, str], int] = {}

    normalized_doi = frame[doi_column].map(normalize_doi)
    normalized_title = frame[title_column].map(normalize_title)
    abstract_hash = frame[abstract_column].map(text_sha256)

    for row_index, (doi, title, abstract) in enumerate(
        zip(normalized_doi, normalized_title, abstract_hash, strict=True)
    ):
        keys: list[tuple[str, str]] = []
        if doi:
            keys.append(("doi", doi))
        if title:
            keys.append(("title", title))
        if normalize_text(frame.iloc[row_index][abstract_column]):
            keys.append(("abstract", abstract))
        for key in keys:
            if key in first_seen:
                union_find.union(row_index, first_seen[key])
            else:
                first_seen[key] = row_index

    roots = [union_find.find(index) for index in range(len(frame))]
    root_to_group = {
        root: group_id for group_id, root in enumerate(dict.fromkeys(roots))
    }
    return pd.Series(
        [root_to_group[root] for root in roots],
        index=frame.index,
        name="duplicate_group_id",
        dtype="int64",
    )


def validate_split_disjointness(
    frame: pd.DataFrame,
    split_column: str = "split",
    group_column: str = "duplicate_group_id",
) -> None:
    """Raise when one duplicate group occurs in more than one split."""
    split_counts = frame.groupby(group_column, dropna=False)[split_column].nunique()
    leaking = split_counts[split_counts > 1]
    if not leaking.empty:
        examples = ", ".join(map(str, leaking.index[:10]))
        raise ValueError(f"Duplicate groups cross split boundaries: {examples}")


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"Unsupported input format: {path.suffix}")


def write_table(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".parquet":
        frame.to_parquet(path, index=False)
    elif path.suffix.lower() == ".csv":
        frame.to_csv(path, index=False)
    else:
        raise ValueError(f"Unsupported output format: {path.suffix}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--title-column", default="title")
    parser.add_argument("--abstract-column", default="abstract")
    parser.add_argument("--doi-column", default="doi")
    args = parser.parse_args()

    frame = read_table(args.input)
    required = {args.title_column, args.abstract_column, args.doi_column}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    frame = frame.copy()
    frame["title_clean"] = frame[args.title_column].map(normalize_text)
    frame["abstract_clean"] = frame[args.abstract_column].map(normalize_text)
    frame["normalized_doi"] = frame[args.doi_column].map(normalize_doi)
    frame["abstract_sha256"] = frame[args.abstract_column].map(text_sha256)
    frame["duplicate_group_id"] = duplicate_components(
        frame,
        doi_column=args.doi_column,
        title_column=args.title_column,
        abstract_column=args.abstract_column,
    )
    write_table(frame, args.output)


if __name__ == "__main__":
    main()
