# MASSK

**Multilevel Adaptive Semantic Scientific Knowledge Model**

MASSK is a notebook-based research project for eight-class classification of scientific publication records. It combines two frozen semantic views, a calibrated PRISM-Evidence base posterior, exact dual-view retrieval, uncertainty estimation, and a compact class-wise retrieval residual.

The executed notebooks are the authoritative implementation. This compact release contains their saved code, outputs and figures, public publication identifiers, original fold assignments, recorded experimental settings, and derived evaluation results. It supports inspection and result tracing; it is not a self-contained fresh-training package. Title/abstract text, author names and institutional affiliations are excluded from the released dataset.

Development validation and retrospective stress evaluation use different fitted predictors. Their configurations and conclusions are distinguished below. See [reproduction scope and provenance](REPRODUCIBILITY.md) for the exact boundary of the release.

## Repository structure

```text
MASSK/
├── Notebooks/
│   ├── 01_data_acquisition_and_audit.ipynb
│   ├── 02_preprocessing_features_and_splits.ipynb
│   ├── 03_baselines_and_comparators.ipynb
│   ├── 04_massk_training_and_ablations.ipynb
│   └── 05_evaluation_and_results.ipynb
├── dataset/
│   └── publication_metadata.parquet
├── data_manifest/
│   ├── publication_ids.csv
│   ├── taxonomy_mapping.csv
│   ├── duplicate_groups.csv
│   ├── split_assignments.csv
│   ├── nested_fold_assignments.csv
│   └── inner_fold_assignments.csv
├── configs/
│   ├── massk.yaml
│   └── prism_evidence.yaml
├── results/
│   ├── development_results.csv
│   ├── temporal_test_results.csv
│   ├── external_test_results.csv
│   ├── per_class_results.csv
│   ├── development_classwise_coefficients.csv
│   ├── stress_classwise_coefficients.csv
│   └── stress_model_fit_audit.csv
├── provenance/
│   ├── notebook_manifest.csv
│   ├── runtime_versions.csv
│   ├── result_sources.csv
│   ├── development_model_mapping.csv
│   └── file_checksums.csv
├── REPRODUCIBILITY.md
├── requirements.txt
├── environment.yml
└── LICENSE
```

## Data sources

The released manifests contain stable source identifiers, direct record URLs, split assignments, taxonomy labels, and duplicate-component membership. Text can be reconstructed from the official services when permitted by the applicable source terms.

| Source | Role | Direct access | Documentation |
|---|---|---|---|
| OpenAlex Works | Primary metadata; temporal cohort; arXiv-hosted external works indexed by OpenAlex | [Works API](https://api.openalex.org/works) | [OpenAlex developers](https://developers.openalex.org/) |
| arXiv metadata | Exposed pilot cohort included in development validation | [Metadata API](https://export.arxiv.org/api/query) | [API user manual](https://info.arxiv.org/help/api/user-manual.html) |
| Semantic Scholar Academic Graph | DOI-based metadata enrichment | [Paper batch endpoint](https://api.semanticscholar.org/graph/v1/paper/batch) | [Academic Graph API](https://api.semanticscholar.org/api-docs/graph) |

OpenAlex makes its complete dataset available under CC0. arXiv records remain subject to the API terms and the license attached to each source record. Semantic Scholar data remain subject to its API and dataset license terms. The MIT license in this repository applies to the source code, not to third-party records.

Thank you to arXiv for use of its open access interoperability.

The retained collection contains 7,446 OpenAlex records, 1,176 directly acquired arXiv pilot records, and 1,181 arXiv-hosted records acquired through OpenAlex. The external cohort uses OpenAlex field labels. Its stable `arxiv:W…` publication IDs are historical IDs; their `W…` record component is an OpenAlex identifier, not an arXiv accession number. `acquisition_service`, `source_url` and `source_api_url` in the publication manifest identify the correct service. Semantic Scholar supplied enrichment for 151 matched records, not additional observations or an independent model cohort.

## Released data

[`dataset/publication_metadata.parquet`](dataset/publication_metadata.parquet) contains one row per retained publication and excludes title, abstract, authors, and institutions. The CSV manifests are directly viewable on GitHub.

| Manifest | Rows | Purpose |
|---|---:|---|
| [`publication_ids.csv`](data_manifest/publication_ids.csv) | 9,803 | Public source IDs, DOI where available, source URLs, year, language, and open-access flag |
| [`taxonomy_mapping.csv`](data_manifest/taxonomy_mapping.csv) | 8 | Stable class IDs, class names, and task-level definitions |
| [`duplicate_groups.csv`](data_manifest/duplicate_groups.csv) | 9,803 | Exact and near-duplicate component membership after deduplication |
| [`split_assignments.csv`](data_manifest/split_assignments.csv) | 9,803 | Train, validation, temporal, and external cohort assignments |
| [`nested_fold_assignments.csv`](data_manifest/nested_fold_assignments.csv) | 13,416 | Original outer holdout assignments: 6,708 publications × 2 repeats, with anonymous author–institution proxy groups |
| [`inner_fold_assignments.csv`](data_manifest/inner_fold_assignments.csv) | 26,832 | Original inner cross-fitting assignments within the six outer-training contexts |

### Corpus composition

| Recorded source/cohort label | Records | Share |
|---|---:|---:|
| OpenAlex | 7,446 | 75.96% |
| arXiv-based records | 2,357 | 24.04% |
| **Total** | **9,803** | **100.00%** |

| Split | Records | Function |
|---|---:|---|
| Train | 3,825 | Initial fixed-split training; later pooled into development |
| Validation | 2,883 | Initial validation, including exposed arXiv pilot; later pooled into development |
| Temporal test | 1,914 | Retrospective OpenAlex 2025 stress evaluation |
| External test | 1,181 | Retrospective source-shift stress evaluation |

The final development comparison pools train and validation into 6,708 unique publications and uses repeated 2 × 3 outer validation. Outer folds are stratified by class label and grouped by a transitive author–institution identity proxy. These proxy groups are distinct from exact/near-duplicate groups; only their anonymous integer IDs are released. Public `publication_id` corresponds to notebook `sample_id`; public `temporal_test` corresponds to the notebook's historical `test` split name.

### Eight-class taxonomy

| ID | Class | Records |
|---:|---|---:|
| 0 | Biochemistry, Genetics and Molecular Biology | 1,219 |
| 1 | Computer Science | 1,032 |
| 2 | Economics, Econometrics and Finance | 1,266 |
| 3 | Engineering | 1,194 |
| 4 | Materials Science | 1,252 |
| 5 | Mathematics | 1,203 |
| 6 | Medicine | 1,420 |
| 7 | Physics and Astronomy | 1,217 |

## Method

1. Normalize identifiers and text using deterministic Unicode, markup, whitespace, and DOI rules.
2. Remove unusable records and resolve transitive exact-duplicate components before assigning splits.
3. Construct the author–institution identity-proxy groups and preserve them during repeated 2 × 3 class-stratified development validation.
4. Encode title and abstract using pinned Qwen3 and SPECTER2 classification representations.
5. Build PRISM-Evidence from independently fitted semantic paths, an interaction path, and a compact evidence router.
6. Retrieve the exact Top-5 neighbours from the applicable training partition using the mean of the two cosine similarities and softmax temperature 0.07.
7. Apply the eight-parameter MASSK residual:

   $$
   z_c = \log p_{\mathrm{PRISM}}(c)
   + \left(1-\max_j p_{\mathrm{PRISM}}(j)\right)\gamma_c
   \left[\log p_{\mathrm{kNN}}(c)-\log p_{\mathrm{PRISM}}(c)\right].
   $$

8. Obtain the final posterior with `softmax(z)` and evaluate discrimination, probability quality, calibration, error ranking, selective risk, retrieval, and class-specific performance.

The eight coefficients are fitted on group-cross-fitted inner-OOF probabilities, with the base predictor fixed. The executed procedure initializes every coefficient at **0.15**, uses **full-batch Adam, learning rate 0.05, exactly 300 iterations**, and retains the state with the lowest observed fitting objective. The objective is class-weighted cross-entropy plus **0.01 × mean(γ²)**, with no patience-based early stopping. Probabilities are clipped to [1e−7, 1] before logarithms. The mean penalty equals `(0.01 / 8) × sum(γ²)`; it is not `0.01 × sum(γ²)`.

Development preprocessing, fitting, calibration and retrieval references follow their respective train/stop/calibration and inner/outer partitions. Stress evaluation instead uses all 6,708 development publications as the retrieval reference after model fixation. The residual multiplier `1 − max(p_base)` is distinct from the diagnostic margin uncertainty `1 − (p_top1 − p_top2)`.

## Development results

The following values use the common 6,708-record development panel. They are post-selection development estimates and should be interpreted as exploratory rather than independent confirmation.

| Model | Accuracy | Balanced accuracy | Macro-F1 | MCC | NLL ↓ | Brier ↓ | ECE-15 ↓ | AURC ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **MASSK class-wise retrieval residual** | **0.8099** | **0.8062** | **0.8057** | **0.7825** | **0.5448** | **0.2789** | 0.0141 | **0.0705** |
| PRISM-Evidence | 0.8093 | 0.8058 | 0.8053 | 0.7819 | 0.5552 | 0.2820 | 0.0163 | 0.0717 |
| Dual-Path control | 0.8087 | 0.8048 | 0.8045 | 0.7812 | 0.5550 | 0.2819 | 0.0139 | 0.0717 |
| Full four-branch control | 0.8084 | 0.8050 | 0.8044 | 0.7808 | 0.5539 | 0.2822 | 0.0175 | 0.0720 |
| Consensus core | 0.8055 | 0.8022 | 0.8014 | 0.7775 | 0.5554 | 0.2835 | **0.0109** | 0.0723 |
| Qwen3 matched head | 0.7971 | 0.7939 | 0.7933 | 0.7678 | 0.5760 | 0.2910 | 0.0229 | 0.0764 |
| SPECTER2 linear | 0.7773 | 0.7736 | 0.7734 | 0.7450 | 0.6408 | 0.3232 | 0.0407 | 0.0904 |
| TF-IDF linear | 0.6674 | 0.6627 | 0.6616 | 0.6193 | 1.0150 | 0.4687 | 0.0455 | 0.1817 |

### Paired MASSK minus PRISM-Evidence effects

| Metric | Difference | 95% interval | Interpretation |
|---|---:|---:|---|
| Macro-F1 | +0.000456 | [-0.002578, +0.003519] | Interval crosses zero; the +0.003 materiality threshold was not reached |
| NLL | -0.010436 | [-0.013422, -0.007382] | Nominal post-selection probability-loss improvement |
| Multiclass Brier score | -0.003123 | [-0.004602, -0.001632] | Nominal post-selection probability-loss improvement |

The classification superiority criterion was not satisfied. The probability-loss differences are useful diagnostic signals but require confirmation on newly acquired data.

## Retrospective stress evaluation

The temporal and external cohorts were excluded from model fitting and tuning, but their label-distribution diagnostics had previously been inspected. They are retrospective stress evaluations, not fully hidden prospective confirmation.

The development PRISM-Evidence router has **six parameters** (one intercept and five evidence coefficients, with class priors removed). The separately fitted retrospective implementation tested a **22-parameter** router. Its activation gate failed in all three fits, yielding an exact **0.5 consensus–interaction blend** with temperature 1.0. The model names below refer to that frozen stress implementation, not to the identical fitted development predictor. The stress correction uses the mean of the six development coefficient vectors and is not fitted on stress labels. See [phase-specific settings](configs/prism_evidence.yaml) and [fit audit](results/stress_model_fit_audit.csv).

| Cohort | Model | Accuracy | Balanced accuracy | Macro-F1 | MCC | NLL ↓ | Brier ↓ | ECE-15 ↓ |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Temporal 2025 | PRISM-Evidence | 0.7732 | 0.7740 | 0.7732 | 0.7413 | 0.6646 | 0.3307 | **0.0433** |
| Temporal 2025 | MASSK | **0.7774** | **0.7782** | **0.7772** | **0.7462** | **0.6614** | **0.3299** | 0.0470 |
| External source shift | PRISM-Evidence | **0.5597** | 0.5604 | **0.5509** | 0.5087 | **1.5147** | **0.6572** | **0.2137** |
| External source shift | MASSK | **0.5597** | **0.5605** | 0.5499 | **0.5092** | 1.5614 | 0.6693 | 0.2367 |

| Cohort | Metric | MASSK − PRISM | 95% paired interval | Result |
|---|---|---:|---:|---|
| Temporal 2025 | Macro-F1 | +0.0040 | [-0.0010, +0.0097] | Uncertain |
| Temporal 2025 | NLL | -0.0031 | [-0.0102, +0.0039] | Uncertain |
| Temporal 2025 | Brier score | -0.0008 | [-0.0042, +0.0024] | Uncertain |
| External source shift | Macro-F1 | -0.0011 | [-0.0088, +0.0058] | Uncertain |
| External source shift | NLL | +0.0467 | [+0.0336, +0.0603] | PRISM-Evidence retained lower loss |
| External source shift | Brier score | +0.0121 | [+0.0072, +0.0173] | PRISM-Evidence retained lower loss |
| External source shift | ECE-15 | +0.0230 | [+0.0164, +0.0301] | PRISM-Evidence retained better calibration |

### Per-class F1

| Class | Temporal PRISM | Temporal MASSK | External PRISM | External MASSK |
|---|---:|---:|---:|---:|
| Biochemistry, genetics and molecular biology | 0.7592 | **0.7746** | **0.5911** | 0.5772 |
| Computer science | 0.7190 | **0.7285** | **0.4789** | 0.4780 |
| Economics, econometrics and finance | 0.8889 | **0.8898** | 0.5146 | **0.5217** |
| Engineering | **0.6765** | 0.6709 | **0.4303** | 0.4228 |
| Materials science | 0.7602 | **0.7661** | 0.6642 | **0.6667** |
| Mathematics | 0.8505 | **0.8518** | 0.6478 | **0.6598** |
| Medicine | **0.7593** | 0.7569 | **0.4422** | 0.4343 |
| Physics and astronomy | 0.7723 | **0.7793** | **0.6385** | **0.6385** |

Full metric rows and confidence intervals are available in [`results/`](results/).

## Retrieval and concept tagging

Retrieval relevance is defined by shared broad thematic class and is therefore a reproducible proxy, not a substitute for expert relevance assessment.

| Retrieval scope | Precision@K | Hit@K | MRR@10 | nDCG@10 |
|---|---:|---:|---:|---:|
| Development dual-view consensus, K=10 | 0.7785 | — | 0.8338 | 0.7807 |
| Temporal 2025, K=5 | 0.6946 | 0.9101 | 0.8031 | 0.6856 |
| External source shift, K=5 | 0.5236 | 0.7341 | 0.6139 | 0.5217 |

Closed-vocabulary concept tagging is evaluated separately from classification:

| Method | F1@10 |
|---|---:|
| Qwen3 embedding linear model | **0.3324** |
| SPECTER2 embedding linear model | 0.3140 |
| TF-IDF linear model | 0.2690 |
| MASSK dual-view consensus | 0.2596 |

The specialized Qwen3 tagging model is the point leader for this endpoint; MASSK is not presented as universally best across tasks.

## Computational profile

| Operation | Scope | Observed value |
|---|---|---:|
| Reusable encoder and exact-index setup | 6,708 reference records | 216.857 s |
| Temporal batch throughput | 1,914 records | 31.08 records/s |
| External batch throughput | 1,181 records | 35.65 records/s |
| Warmed batch-1 latency | Temporal, 32 queries; median / P95 | 64.10 / 84.10 ms |
| Warmed batch-1 latency | External, 32 queries; median / P95 | 67.50 / 87.46 ms |
| Conservative GPU-memory upper bound | Main process + SPECTER2 worker | 3.764 GiB |
| Peak process RAM | Complete benchmark session | 2.731 GiB |

These measurements concern the separately fitted retrospective implementation and include tokenization, both semantic encoders, PRISM-Evidence, exact Top-5 retrieval, and the class-wise residual. They were recorded on an NVIDIA GeForce RTX 5070 Laptop GPU. They do not establish training time or raw-text inference time for the exact development predictor. Fresh-versus-cached inference agreed on all predicted labels, but posterior probabilities differed by up to 0.002730; this is not bitwise reproduction.

## Notebooks

| Notebook | Purpose |
|---|---|
| [`01_data_acquisition_and_audit.ipynb`](Notebooks/01_data_acquisition_and_audit.ipynb) | Source acquisition, schema audit, cohort design, and provenance |
| [`02_preprocessing_features_and_splits.ipynb`](Notebooks/02_preprocessing_features_and_splits.ipynb) | Cleaning, deduplication, leakage checks, split construction, and feature preparation |
| [`03_baselines_and_comparators.ipynb`](Notebooks/03_baselines_and_comparators.ipynb) | Classical, embedding-based, and transformer comparator evaluation |
| [`04_massk_training_and_ablations.ipynb`](Notebooks/04_massk_training_and_ablations.ipynb) | MASSK development, group-safe validation, ablations, and statistical gates |
| [`05_evaluation_and_results.ipynb`](Notebooks/05_evaluation_and_results.ipynb) | Final tables, retrospective stress evaluation, retrieval, calibration, and efficiency |

The notebooks preserve the original executed analysis record, including intermediate and rejected configurations. Their current files are byte-for-byte copies of the reviewed source notebooks; [SHA-256 hashes and code/output counts](provenance/notebook_manifest.csv) identify this release. No replacement training implementation is provided. YAML files describe the recorded experiments and are not consumed as executable notebook configurations.

## Viewing the notebooks and data

The root dependency files install an **inspection environment only**. They do not recreate the research GPU environments or make every historical notebook cell runnable from this compact download.

Using Conda:

```bash
conda env create -f environment.yml
conda activate massk-inspect
jupyter lab Notebooks
```

Using `venv`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter lab Notebooks
```

## Recorded execution environments

| Scope | Recorded environment |
|---|---|
| Development residual replay | Python 3.12.3; PyTorch 2.12.1+cu130; CUDA 13.0; RTX 5070 Laptop GPU |
| Qwen3 main process in the raw-text benchmark | Transformers 5.12.1; Sentence-Transformers 5.6.0 |
| Separate SPECTER2 adapter worker | Transformers 4.57.6; Adapters 1.3.0 |
| Tokenizer version recorded for both benchmark runtimes | Tokenizers 0.22.2 |

These are observed version records, not newly tested installation lockfiles. The two Transformers runtimes must not be collapsed into a single environment when describing the recorded benchmark. Full records are in [`provenance/runtime_versions.csv`](provenance/runtime_versions.csv).

## Reproduction scope

Open the notebooks to inspect saved code, tables and figures. Use the public manifests to trace publications and the exact published outer/inner assignments; use [`provenance/result_sources.csv`](provenance/result_sources.csv) to locate result-producing notebook sections.

A fresh end-to-end run additionally needs the original permitted title/abstract snapshots, feature caches, fitted model artifacts and referenced experiment helpers, plus the original directory layout and appropriate GPU runtimes. Those complete runtime assets are not included here. Fetching current source records by ID may return changed metadata and is not an exact reconstruction of the acquisition snapshot. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) before attempting a rerun.

## Evidence boundaries

- Development values are repeated group-stratified estimates from a reused development panel.
- Temporal and external values are retrospective stress evaluations.
- No result in this repository establishes universal model superiority.
- Retrieval relevance uses broad-class agreement as a proxy.
- Controlled title-only, truncated-abstract, and token-noise evaluations were not performed in the recorded experiments.
- Independent confirmation requires a newly acquired cohort collected after the full protocol and model configuration are fixed.

## License

Source code is released under the [MIT License](LICENSE). Dataset identifiers and metadata remain governed by their original providers and record-level licenses.
