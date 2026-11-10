# MASSK

**Multilevel Adaptive Semantic Scientific Knowledge Model**

MASSK is a notebook-based research project for eight-class classification of scientific publication records. It combines two frozen semantic views, a calibrated PRISM-Evidence base posterior, exact dual-view retrieval, uncertainty estimation, and a compact class-wise retrieval residual.

The executed notebooks are the authoritative implementation. This compact release contains their saved code, outputs and figures, public publication identifiers, original fold assignments, recorded experimental settings, and derived evaluation results. It supports inspection and result tracing; it is not a self-contained fresh-training package. Title/abstract text, author names and institutional affiliations are excluded from the released dataset.

Development validation and retrospective stress evaluation use different fitted predictors. Their configurations and conclusions are distinguished below. See [reproduction scope and provenance](REPRODUCIBILITY.md) for the exact boundary of the release.

Notebook 06 (run `rev01`) adds a controlled study of the correction: ablations of its two elements, calibration controls, a stress evaluation in which the base and the correction follow one specification, raw-text perturbations, computational cost, topic-level relevance of the retrieved neighbours, and a prespecified confirmation on newly acquired publications. Its results are summarised in [Revision analyses](#revision-analyses-run-rev01); where its conclusions differ from the earlier sections, the differences are stated there.

## Repository structure

```text
MASSK/
├── Notebooks/
│   ├── 01_data_acquisition_and_audit.ipynb
│   ├── 02_preprocessing_features_and_splits.ipynb
│   ├── 03_baselines_and_comparators.ipynb
│   ├── 04_massk_training_and_ablations.ipynb
│   ├── 05_evaluation_and_results.ipynb
│   └── 06_revision_ablations_and_corrected_evaluation.ipynb
├── dataset/
│   └── publication_metadata.parquet
├── data_manifest/
│   ├── publication_ids.csv
│   ├── taxonomy_mapping.csv
│   ├── duplicate_groups.csv
│   ├── split_assignments.csv
│   ├── confirmation_cohort_ids.csv
│   ├── nested_fold_assignments.csv
│   └── inner_fold_assignments.csv
├── configs/
│   ├── massk.yaml
│   ├── prism_evidence.yaml
│   ├── rev01_experiment.yaml
│   └── rev01_environment.yaml
├── docs/
│   └── research_protocol_rev01.md
├── results/
│   ├── development_results.csv
│   ├── temporal_test_results.csv
│   ├── external_test_results.csv
│   ├── per_class_results.csv
│   ├── development_classwise_coefficients.csv
│   ├── stress_classwise_coefficients.csv
│   ├── stress_model_fit_audit.csv
│   ├── tables/rev01/      # tables of Notebook 06 (CSV, LaTeX), figure data, result registry
│   └── figures/rev01/     # five figures (PNG, PDF)
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
| [`confirmation_cohort_ids.csv`](data_manifest/confirmation_cohort_ids.csv) | 2,940 | Identifiers, year and class of the confirmation cohort acquired on 10 November 2026; these publications are not part of the 9,803 corpus records |

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

## Revision analyses (run rev01)

Notebook 06 re-examines the correction under a protocol written in three parts, each before the corresponding analyses were executed ([protocol](docs/research_protocol_rev01.md), [settings](configs/rev01_experiment.yaml)). The development and stress analyses are post hoc or retrospective: the development panel had already been used for model selection, and both stress cohorts had been evaluated before. The confirmation on newly acquired publications is the only prespecified test. NLL is the primary endpoint. In this section Δ > 0 favours the first-named variant; for losses this is the opposite of the sign used in the two sections above, where differences are MASSK − PRISM-Evidence. Intervals are 95% percentile intervals of a paired paper-level bootstrap with 20,000 resamples; p-values are two-sided bootstrap values adjusted by the Holm method within each family.

| ID | Variant | Corrected logits | Parameters |
|---|---|---|---:|
| V0 | PRISM-Evidence | log p_b | 0 |
| V1 | MASSK (Full) | log p_b + u·γ_c·(log p_k − log p_b), u = 1 − max p_b | 8 |
| V2 | Shared γ | as V1 with one γ | 1 |
| V3 | No multiplier | as V1 with u = 1 | 8 |
| V4 | Shared γ, no multiplier | log-linear interpolation with a constant weight | 1 |
| V5 | kNN only | log p_k | 0 |
| C1 | Temperature scaling | log p_b / τ | 1 |
| C2 | Class bias | log p_b + b_c | 8 |
| C3 | Vector scaling | a_c·log p_b + b_c | 16 |

Here p_b is the PRISM-Evidence posterior and p_k the top-5 neighbour class distribution. All learned variants are fitted on identical inner-OOF rows with the procedure described under [Method](#method).

### Development panel

Posteriors are averaged over the two repeats for each of the 6,708 publications ([Table 6.5](results/tables/rev01/table6_5_primary_family.csv)).

| MASSK (V1) compared with | ΔNLL | 95% interval | Holm p | Reading |
|---|---:|---:|---:|---|
| PRISM-Evidence (V0) | +0.0104 | [+0.0074, +0.0134] | < 0.001 | The correction lowers NLL |
| Temperature scaling (C1) | +0.0077 | [+0.0048, +0.0106] | < 0.001 | The gain exceeds recalibration |
| Class bias (C2) | +0.0129 | [+0.0097, +0.0161] | < 0.001 | The gain exceeds recalibration |
| Vector scaling (C3) | +0.0084 | [+0.0051, +0.0117] | < 0.001 | The gain exceeds recalibration |
| Shared γ (V2) | −0.0006 | [−0.0017, +0.0005] | 0.547 | Class-specific coefficients are not supported |
| No multiplier (V3) | −0.0010 | [−0.0026, +0.0006] | 0.547 | The confidence multiplier is not supported |
| Shared γ, no multiplier (V4) | −0.0012 | [−0.0031, +0.0006] | 0.547 | Neither element is supported |

The retrieval-conditioned correction improves probability quality beyond three recalibration controls. One shared coefficient without the confidence multiplier is statistically indistinguishable from the eight-coefficient form and has the lower point NLL. Macro-F1 does not change materially in any comparison.

- **Pilot cohort.** On the 5,532 OpenAlex rows the gain over PRISM-Evidence is +0.0099 [+0.0065, +0.0133] with the full retrieval index and +0.0133 [+0.0105, +0.0161] when the 1,176 arXiv pilot rows are removed from every index and the coefficients are refitted ([Table 6.9](results/tables/rev01/table6_9_pilot_exclusion.csv)).
- **Sensitivity.** MASSK has a lower NLL than PRISM-Evidence in 15 of 16 settings of the neighbour count, the softmax temperature and the probability floor ([Figure 6.2](results/figures/rev01/png/figure6_2_sensitivity.png)).
- **Frozen retrieval.** With the frozen vectors and no label training, nDCG@10 is 0.7077 for the dual view, 0.7070 for Qwen3 alone and 0.6832 for SPECTER2 alone, as means over the six outer contexts ([Table 6.8](results/tables/rev01/table6_8_frozen_retrieval.csv)).

### Stress evaluation with one specification

The base posterior follows the recorded stress specification, an equal blend of the consensus and interaction paths. B0 is the frozen recorded model, B1 a refit on the same rows, and B2 a refit without the arXiv pilot rows, so that B2 contains no publication later than 2024. For each base the correction and the controls are fitted on the stop rows of that base, and its fit rows form the retrieval index. B2 is the primary base ([Table 6.13](results/tables/rev01/table6_13_stress_primary_family.csv)).

| Cohort | Comparison | ΔNLL | 95% interval | Holm p |
|---|---|---:|---:|---:|
| Temporal 2025 | V1 against V0 | +0.0014 | [−0.0046, +0.0068] | > 0.999 |
| Temporal 2025 | V1 against C1 | +0.0023 | [−0.0034, +0.0076] | > 0.999 |
| Temporal 2025 | V4 against V0 | +0.0010 | [−0.0026, +0.0045] | > 0.999 |
| Temporal 2025 | V4 against C1 | +0.0019 | [−0.0012, +0.0050] | 0.858 |
| External arXiv 2024 | V1 against V0 | −0.0546 | [−0.0737, −0.0369] | < 0.001 |
| External arXiv 2024 | V1 against C1 | −0.0342 | [−0.0531, −0.0167] | < 0.001 |
| External arXiv 2024 | V4 against V0 | −0.0422 | [−0.0494, −0.0352] | < 0.001 |
| External arXiv 2024 | V4 against C1 | −0.0218 | [−0.0276, −0.0161] | < 0.001 |

The development gain does not transfer. The correction is neutral on the temporal cohort and increases NLL on the external cohort for every base: ΔNLL of V1 against V0 is −0.0514, −0.0534 and −0.0546 for B0, B1 and B2 ([Table 6.14](results/tables/rev01/table6_14_stress_across_bases.csv)). Two observations qualify the earlier stress tables:

- The temporal NLL of the base is 0.6646 for the frozen model B0 and 0.6856 for its refit B1 on the same rows. This difference of 0.0210 between two fits exceeds the effect of the correction on that cohort.
- Removing the pilot rows lowers the external macro-F1 of the base from 0.5509 (B0) to 0.4863 (B2), which is consistent with the pilot rows having acted as same-source training data for the arXiv-hosted cohort.

### Raw-text perturbations and cost

The queries of the temporal cohort were re-encoded from raw text under six conditions with base B2; the models and the retrieval index were unchanged. Fresh and stored embeddings of the clean texts agree, with a mean cosine of 0.99991 for Qwen3 and 0.99999 for SPECTER2 ([Table 6.18](results/tables/rev01/table6_18_encoder_check.csv), [Table 6.19](results/tables/rev01/table6_19_text_perturbations.csv)).

| Condition | Macro-F1 (V0) | NLL (V0) | ΔNLL, V1 against V0 | 95% interval |
|---|---:|---:|---:|---:|
| Clean, re-encoded | 0.7754 | 0.6597 | +0.0016 | [−0.0043, +0.0070] |
| Title only | 0.7585 | 0.6840 | +0.0111 | [+0.0048, +0.0169] |
| Abstract cut to the first 50% of words | 0.7764 | 0.6585 | +0.0044 | [−0.0013, +0.0096] |
| Abstract cut to the first 25% of words | 0.7719 | 0.6630 | +0.0040 | [−0.0023, +0.0097] |
| Random deletion of 10% of words | 0.7715 | 0.6602 | +0.0009 | [−0.0052, +0.0064] |
| Random deletion of 30% of words | 0.7689 | 0.6709 | +0.0046 | [−0.0010, +0.0099] |

The interval of the correction excludes zero only in the title-only condition. These results are descriptive, and the external cohort was not perturbed.

On an Apple M1 Pro with 16 GB the evaluated system needs 308.4 ms per publication, of which the two frozen encoders account for 99.98%; the base posterior takes 0.035 ms, and exact top-5 retrieval with the correction 0.014 ms per publication ([Table 6.20](results/tables/rev01/table6_20b_cost_inference.csv)). These values are not comparable with the GPU measurements in the [computational profile](#computational-profile).

### Prespecified confirmation on newly acquired publications

The third part of the protocol tests the in-distribution effect once on publications that no earlier analysis had used. The evaluated system (base B2 with V1, V4 and C1) was stored on 10 November 2026 at 13:25:50 UTC. The SHA-256 of the stored file, `c5adf21f83d0829e8aa731558e8b69bb538e1fa9b869814b7154e8e32f564ef6`, was registered in the protocol and in the settings at 13:26:19 UTC, before the first record was requested (13:26:43 UTC); nothing was refitted afterwards. The cohort was requested from OpenAlex with the filter of the development acquisition (2018 to 2024) and three seeds per class that had not been used before. Of the 4,800 records, 2,940 publications remained after the unchanged eligibility and duplicate rules and the removal of matches with the corpus ([identifiers](data_manifest/confirmation_cohort_ids.csv), [Table 6.24](results/tables/rev01/table6_24_confirmation_flow.csv)).

| Variant | Against | ΔNLL | 95% interval | Holm p | Outcome |
|---|---|---:|---:|---:|---|
| V4, one shared coefficient | V0, base | +0.0100 | [+0.0076, +0.0123] | < 0.001 | Confirmed |
| V4, one shared coefficient | C1, temperature scaling | +0.0075 | [+0.0054, +0.0097] | < 0.001 | Confirmed |
| V1, class-wise with multiplier | V0, base | +0.0053 | [+0.0008, +0.0095] | 0.044 | Not confirmed |
| V1, class-wise with multiplier | C1, temperature scaling | +0.0028 | [−0.0015, +0.0070] | 0.195 | Not confirmed |

A variant is confirmed only if it is favoured over both the base and temperature scaling after the Holm adjustment and the lower bound of ΔMacro-F1 against the base is at least −0.003 ([Table 6.27](results/tables/rev01/table6_27_confirmation_primary_family.csv)). The one-coefficient correction passes this rule; the class-wise form with the multiplier does not, because it does not exceed temperature scaling. The gain of V4 grows with the similarity to the nearest index publication, from +0.0039 in the two lowest quintiles to +0.0154 and +0.0156 in the two highest ([Table 6.28](results/tables/rev01/table6_28_confirmation_subgroups.csv)). [Figure 6.5](results/figures/rev01/png/figure6_5_gain_across_cohorts.png) places the development, confirmation, temporal and external estimates side by side. The cohort is a new sample from the service that supplied the fit rows, so it tests the in-distribution effect only.

### Topic-level relevance and label stability

- **Topic-level relevance.** For the 5,532 OpenAlex publications of the development panel, 37.9% of the ten nearest neighbours share the subfield of the query and 20.4% share its primary topic, against 24.3% and 1.5% for a random index publication of the same class. Among the queries with a coupled publication in the index, 11.4% of the neighbours share a referenced work with the query, against 0.9% for a random publication of the same class ([Table 6.21](results/tables/rev01/table6_21a_topic_relevance.csv)). Topics are assigned automatically by OpenAlex; no expert judged relevance.
- **Label stability.** On 10 November 2026 OpenAlex reported the stored field for 67.28% of these publications, another of the eight fields for 12.56% and a field outside the eight classes for 17.53%; 2.62% had no current field ([Table 6.29](results/tables/rev01/table6_29_label_stability.csv)). The confirmation cohort carries the November labels, whereas the fit rows carry the July labels. A post hoc breakdown relates the development predictions to the current label state ([Table 6.30](results/tables/rev01/table6_30_development_by_label_state.csv)).

### Summary

On the development panel the correction yields a small gain in probability quality that recalibration alone does not reproduce. Its class-specific and confidence-weighted form is not needed: the one-coefficient form was confirmed on newly acquired publications and the class-wise form was not. The gain does not carry over to later or differently sourced publications. The release therefore documents a controlled experimental study of the correction and makes no claim of a deployable improvement. All findings are listed in [`nb06_findings.csv`](results/tables/rev01/nb06_findings.csv), and [`result_registry.csv`](results/tables/rev01/result_registry.csv) links each table and figure to its notebook section.

## Retrieval and concept tagging

Retrieval relevance is defined by shared broad thematic class and is therefore a reproducible proxy, not a substitute for expert relevance assessment.

| Retrieval scope | Precision@K | Hit@K | MRR@10 | nDCG@10 |
|---|---:|---:|---:|---:|
| Development dual-view consensus, K=10 | 0.7785 | — | 0.8338 | 0.7807 |
| Temporal 2025, K=5 | 0.6946 | 0.9101 | 0.8031 | 0.6856 |
| External source shift, K=5 | 0.5236 | 0.7341 | 0.6139 | 0.5217 |

The development row was produced in Notebook 04 with projection heads trained on class labels; it does not describe the frozen similarity used by the correction. The values for the frozen vectors are given in [Table 6.8](results/tables/rev01/table6_8_frozen_retrieval.csv) and in the section above.

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
| [`06_revision_ablations_and_corrected_evaluation.ipynb`](Notebooks/06_revision_ablations_and_corrected_evaluation.ipynb) | Run `rev01`: mechanism ablations, calibration controls, single-specification stress evaluation, raw-text perturbations, cost, topic-level relevance, and prespecified confirmation |

The notebooks preserve the original executed analysis record, including intermediate and rejected configurations. Their current files are byte-for-byte copies of the reviewed source notebooks; [SHA-256 hashes and code/output counts](provenance/notebook_manifest.csv) identify this release. No replacement training implementation is provided. The files `massk.yaml` and `prism_evidence.yaml` describe the recorded experiments and are not consumed as executable notebook configurations. Notebook 06 reads `rev01_experiment.yaml`, which the original layout stores as `Configs/rev01_experiment.yaml`.

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
| Notebook 06 (run `rev01`) | Python 3.11.15; PyTorch 2.11.0; Transformers 5.7.0; Tokenizers 0.22.2; NumPy 2.4.4; pandas 2.3.3; SciPy 1.16.3; scikit-learn 1.8.0; Requests 2.33.1; Matplotlib 3.10.9; Apple M1 Pro, 16 GB; encoders on the Apple GPU, other stages on CPU |

These are observed version records, not newly tested installation lockfiles. The two Transformers runtimes must not be collapsed into a single environment when describing the recorded benchmark. Full records are in [`provenance/runtime_versions.csv`](provenance/runtime_versions.csv) and, for Notebook 06, in [`configs/rev01_environment.yaml`](configs/rev01_environment.yaml).

## Reproduction scope

Open the notebooks to inspect saved code, tables and figures. Use the public manifests to trace publications and the exact published outer/inner assignments; use [`provenance/result_sources.csv`](provenance/result_sources.csv) to locate result-producing notebook sections.

A fresh end-to-end run additionally needs the original permitted title/abstract snapshots, feature caches, fitted model artifacts and referenced experiment helpers, plus the original directory layout and appropriate GPU runtimes. Those complete runtime assets are not included here. Fetching current source records by ID may return changed metadata and is not an exact reconstruction of the acquisition snapshot. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) before attempting a rerun.

## Evidence boundaries

- Development values are repeated group-stratified estimates from a reused development panel.
- Temporal and external values are retrospective stress evaluations.
- No result in this repository establishes universal model superiority.
- Retrieval relevance uses broad-class agreement as a proxy.
- Controlled title-only, truncated-abstract and word-deletion evaluations were run only for the temporal cohort (Notebook 06) and are descriptive.
- Steps 1 and 2 of Notebook 06 are post hoc or retrospective; they reuse the development panel and two cohorts that had been evaluated before.
- The prespecified confirmation uses a new sample from the service and years of the fit rows. It supports the in-distribution effect of the one-coefficient correction only.
- OpenAlex labels are not stable: the stored field was still reported for 67.28% of the development publications after four months.
- Topic-level relevance relies on automatically assigned topics and on shared references; no expert judged relevance.
- Transfer to other sources, languages and finer taxonomies has not been confirmed and requires its own validation.

## License

Source code is released under the [MIT License](LICENSE). Dataset identifiers and metadata remain governed by their original providers and record-level licenses.
