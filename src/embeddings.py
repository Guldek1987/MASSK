"""Frozen transformer embedding extraction with pinned model revisions."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yaml


@dataclass(frozen=True)
class EncoderSpec:
    model: str
    revision: str
    pooling: str
    normalize: bool = True
    max_length: int = 512
    batch_size: int = 32
    prefix: str = ""
    separator: str = " "
    adapter: str | None = None
    adapter_revision: str | None = None

    @classmethod
    def from_mapping(cls, values: dict) -> "EncoderSpec":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: values[key] for key in allowed if key in values})


def compose_texts(
    titles: Iterable[object],
    abstracts: Iterable[object],
    prefix: str = "",
    separator: str = " ",
) -> list[str]:
    """Create deterministic title/abstract inputs for an encoder."""
    texts = []
    for title, abstract in zip(titles, abstracts, strict=True):
        title_text = "" if pd.isna(title) else str(title).strip()
        abstract_text = "" if pd.isna(abstract) else str(abstract).strip()
        texts.append(prefix + title_text + separator + abstract_text)
    return texts


def last_token_pool(hidden_state, attention_mask):
    """Pool the last non-padding token for left- or right-padded batches."""
    import torch

    if torch.all(attention_mask[:, -1] == 1):
        return hidden_state[:, -1]
    sequence_lengths = attention_mask.sum(dim=1) - 1
    batch_indices = torch.arange(hidden_state.shape[0], device=hidden_state.device)
    return hidden_state[batch_indices, sequence_lengths]


class FrozenTextEncoder:
    """Minimal inference wrapper for base models and optional adapters."""

    def __init__(self, spec: EncoderSpec, device: str | None = None) -> None:
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.spec = spec
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(
            spec.model,
            revision=spec.revision,
            trust_remote_code=True,
        )
        self.model = AutoModel.from_pretrained(
            spec.model,
            revision=spec.revision,
            trust_remote_code=True,
        )

        if spec.adapter:
            import adapters

            adapters.init(self.model)
            adapter_kwargs = {"source": "hf", "set_active": True}
            if spec.adapter_revision:
                adapter_kwargs["revision"] = spec.adapter_revision
            try:
                self.model.load_adapter(spec.adapter, **adapter_kwargs)
            except TypeError:
                adapter_kwargs.pop("revision", None)
                self.model.load_adapter(spec.adapter, **adapter_kwargs)

        self.model.eval()
        self.model.to(self.device)

    def encode(self, texts: list[str]) -> np.ndarray:
        import torch
        import torch.nn.functional as functional

        batches: list[np.ndarray] = []
        for start in range(0, len(texts), self.spec.batch_size):
            batch_texts = texts[start : start + self.spec.batch_size]
            tokens = self.tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=self.spec.max_length,
                return_tensors="pt",
            )
            tokens = {key: value.to(self.device) for key, value in tokens.items()}
            with torch.inference_mode():
                output = self.model(**tokens).last_hidden_state
                if self.spec.pooling == "last_token":
                    pooled = last_token_pool(output, tokens["attention_mask"])
                elif self.spec.pooling == "cls":
                    pooled = output[:, 0]
                elif self.spec.pooling == "mean":
                    mask = tokens["attention_mask"].unsqueeze(-1)
                    pooled = (output * mask).sum(dim=1) / mask.sum(dim=1).clamp_min(1)
                else:
                    raise ValueError(f"Unsupported pooling mode: {self.spec.pooling}")
                if self.spec.normalize:
                    pooled = functional.normalize(pooled, p=2, dim=1)
            batches.append(pooled.float().cpu().numpy())
        return np.concatenate(batches, axis=0)


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/massk.yaml"))
    parser.add_argument("--encoder", choices=["qwen", "specter2"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ids-output", type=Path)
    parser.add_argument("--id-column", default="publication_id")
    parser.add_argument("--title-column", default="title")
    parser.add_argument("--abstract-column", default="abstract")
    parser.add_argument("--device")
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    spec = EncoderSpec.from_mapping(config["encoders"][args.encoder])
    frame = read_table(args.input)
    required = {args.id_column, args.title_column, args.abstract_column}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    texts = compose_texts(
        frame[args.title_column],
        frame[args.abstract_column],
        prefix=spec.prefix,
        separator=spec.separator,
    )
    embeddings = FrozenTextEncoder(spec, device=args.device).encode(texts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.save(args.output, embeddings)

    ids_output = args.ids_output or args.output.with_suffix(".ids.csv")
    pd.DataFrame(
        {"row_index": np.arange(len(frame)), args.id_column: frame[args.id_column]}
    ).to_csv(ids_output, index=False)


if __name__ == "__main__":
    main()
