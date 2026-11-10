# Research protocol — revision run rev01

Written on 2026-11-05 (14:05 UTC), before any rev01 analysis was executed. Executed in `notebooks/06_revision_ablations_and_corrected_evaluation.ipynb`.

## Evidential status

The rev01 analyses are post hoc. They come after the original 14 refinement rounds on the same 6,708-publication development panel and after reviewer feedback. All rev01 results are exploratory development evidence. None of them is a confirmatory test. NLL is the primary rev01 endpoint because the remaining manuscript claim concerns probability quality. This designation was made after the development NLL results of round 14 had been observed; that order is disclosed rather than concealed. The temporal and external stress cohorts are not opened in rev01.

## Fixed inputs

| Input | Source |
|---|---|
| Labels, sources, years | `dataset/unified/development_dataset.parquet` (6,708 rows) |
| Frozen embeddings | `development_semantic_qwen3_instruction.npy` (1024-d), `development_semantic_specter2_classification.npy` (768-d), L2-normalised |
| Outer folds | `results/tables/nested_fold_assignments.parquet`: 2 repeats × 3 folds |
| Inner folds | `inner_fold` in `results/tables/massk_round10_inner_path_oof.parquet` |
| Base posterior, inner OOF | `results/tables/massk_round12_prism_inner_oof.parquet` |
| Base posterior, outer | `results/tables/massk_prism_evidence_outer_predictions.parquet` (mean of three router seeds) |

## Research questions and hypotheses

- **RQ1 — mechanism.** Do the class-specific coefficients and the confidence multiplier contribute to probability quality, compared with simpler variants fitted on identical inner-OOF rows?
  - H1a: Full has a lower outer NLL than the shared-γ variant.
  - H1b: Full has a lower outer NLL than the class-wise variant without the multiplier.
  - H1c: Full has a lower outer NLL than the shared-γ variant without the multiplier.
- **RQ2 — retrieval versus recalibration.** Does retrieval evidence improve probability quality beyond recalibration alone?
  - H2: Full has a lower outer NLL than each control: temperature scaling (1 parameter), class bias (8 parameters, equal count), vector scaling (16 parameters).
- **RQ3 — sensitivity.** Is the effect stable across the neighbour count k, the softmax temperature T, and the probability floor ε?
- **RQ4 — retrieval quality.** What retrieval quality does the frozen dual-view similarity of Eq. (3) achieve, compared with single views, when the vectors involve no label training?
- **RQ5 — pilot cohort.** Does the effect persist when the 1,176 arXiv records dated 2026 are excluded from the retrieval index and from evaluation?
- **RQ6 — dependence.** Is the effect concentrated in queries whose nearest training neighbour is almost identical?

## Variants

All learned variants use the round-14 fitting procedure:
- fitting rows: inner OOF of each outer-training context;
- retrieval index for fitting: other inner folds;
- class-weighted cross-entropy with weights n/(8·n_c);
- full-batch Adam, learning rate 0.05, 300 iterations;
- the state with the lowest observed objective is kept.

The penalty 0.01·mean(θ²) applies to the γ parameters. Outer predictions use the outer-training rows as the retrieval index.

| ID | Variant | Corrected logits | Parameters |
|---|---|---|---|
| V0 | PRISM-Evidence | log p_b | 0 |
| V1 | MASSK (Full) | log p_b + u·γ_c·(log p_k − log p_b), u = 1 − max p_b | 8 |
| V2 | Shared γ | as V1 with one γ | 1 |
| V3 | No multiplier | as V1 with u = 1 | 8 |
| V4 | Shared γ, no multiplier | log-linear interpolation with constant weight | 1 |
| V5 | kNN only | log p_k | 0 |
| C1 | Temperature scaling | log p_b / τ | 1 |
| C2 | Class bias | log p_b + b_c | 8 |
| C3 | Vector scaling | a_c·log p_b + b_c | 16 |

Default retrieval settings: k = 5, T = 0.07, ε = 1e−7.

## Estimands and metrics

- **E1 (headline):** posteriors are averaged over the two repeats for each publication, then metrics are computed on the 6,708 papers.
- **E2:** metrics are computed in each of the six outer contexts and reported as mean ± SD, with fold wins.
- **Primary endpoint:** E1 NLL.
- **Secondary endpoints:** macro-F1, multiclass Brier score, ECE (15 equal-width bins), accuracy, MCC.
- **Sign convention:** Δ > 0 favours Full. For losses Δ = M_variant − M_Full; for scores Δ = M_Full − M_variant.

## Statistical protocol

- Paired paper-level bootstrap: B = 20,000, seed 20261105, 95% percentile intervals. The proxy-cluster bootstrap is not repeated, because 98.4% of the groups are singletons.
- **Primary family:** Full versus V0, V2, V3, V4, C1, C2, C3 on E1 NLL, seven comparisons.
  - Two-sided bootstrap p-value: p = min(1, 2·min(P*(Δ ≤ 0), P*(Δ ≥ 0))).
  - Holm correction at α = 0.05.
- Secondary endpoints and RQ3–RQ6 are reported descriptively, with unadjusted intervals.

## Decision rules (fixed before execution)

- **Component retention (RQ1).** A component is supported if the Holm-adjusted primary comparison favours Full (Δ_NLL > 0, adjusted p < 0.05) and the lower 95% bound of Δ_macro-F1 is at least −0.003.
- **Retrieval beyond recalibration (RQ2).** The claim is supported only if Full beats every calibration control (C1–C3) under the same rule.
- **Reporting.** If a rule fails, the manuscript reports the failure and removes the corresponding claim.

## Sensitivity grid (RQ3)

One factor is changed at a time from the default; γ is refitted for each setting. The grid is reported descriptively, and the default is retained whatever the result.

| Factor | Values |
|---|---|
| k | {1, 3, 5, 10, 20, 50} |
| T | {0.02, 0.05, 0.07, 0.10, 0.20, 0.50} |
| ε | {1e−7, 1e−5, 1e−3, 1e−2} |

## Retrieval (RQ4)

- Similarity: frozen L2-normalised vectors, either the dual-view mean cosine (Eq. 3), Qwen3 only, or SPECTER2 only.
- Queries are the outer-held rows. The index is the outer-training rows. Relevance is the same thematic class.
- Metrics: nDCG@10, Precision@10, MRR@10, as mean ± SD over six contexts.

## Pilot exclusion (RQ5) and dependence (RQ6)

- **RQ5(a):** V0 and V1 are evaluated on OpenAlex rows only (n = 5,532).
- **RQ5(b):** γ is refitted with the pilot rows removed from every retrieval index, then evaluated on OpenAlex rows.
- **Limitation:** PRISM-Evidence itself was trained with the pilot rows, so its retraining is out of scope for rev01.
- **RQ6:** for each held-out paper, the maximum dual-view cosine to the outer-training rows is computed. ΔNLL(V0 − V1) is reported by quintile of this similarity, with bootstrap intervals.

## Reproduction check

Before the analyses, V1 is recomputed on CPU and compared with `massk_round14_outer_predictions.parquet`. The maximum absolute probability difference must be below 1e−3, the tolerance of the original replay.

## Notation

| Symbol | Meaning |
|---|---|
| p_b | PRISM-Evidence posterior |
| p_k | top-k neighbour class distribution (Eq. 4) |
| u | confidence multiplier, 1 − max p_b |
| γ_c | class-wise correction coefficient, sigmoid of a raw parameter |
| ε | probability floor before taking logarithms |
| k, T | neighbour count and softmax temperature |

## Deviations recorded during execution

| Date | Item | Deviation | Handling |
|---|---|---|---|
| 2026-11-10 | Reproduction check | The coefficients refitted on CPU differ from the recorded GPU-fitted coefficients by up to 5.8e−4. The resulting posteriors exceed the 1e−3 tolerance in 7 of 13,416 outer-held rows (maximum 1.15e−3). With the recorded coefficients, the implementation reproduces the recorded posteriors exactly. | The tolerance is not changed and is reported as not met for the refit. The check is reported in two parts (Table 6.2). All variants use coefficients fitted in notebook 06 on one device. |

---

# Step 2 of run rev01: single-implementation stress evaluation, raw-text perturbations and cost

Written on 2026-11-10, after step 1 was executed and before any step-2 computation. Executed as additional sections of `notebooks/06_revision_ablations_and_corrected_evaluation.ipynb`.

## Evidential status

The temporal (OpenAlex 2025, n = 1,914) and external (arXiv-hosted, 2024, n = 1,181) cohorts were evaluated before, and their recorded results are known: on the external cohort the recorded correction worsened NLL, Brier score and ECE. Step 2 is therefore retrospective. It cannot confirm a benefit. Its purpose is to evaluate one fully specified system on both cohorts and to describe when the correction helps.

## S. Stress evaluation with one implementation

**Base posterior.** The base is the recorded stress specification:
- three seeds each of the Qwen3 path, the SPECTER2 path and the interaction path, with the recorded hyperparameters;
- consensus: the mean over seeds of the average of the two single-view posteriors;
- interaction: the mean over seeds of the temperature-scaled interaction posteriors, with the temperature fitted on the stop rows;
- base posterior: the equal blend of consensus and interaction.

The evidence router is not part of the evaluated system, because it failed its activation gate in the recorded fit.

| ID | Base | Fit rows | Stop rows |
|---|---|---|---|
| B0 | Frozen recorded model (fitted on a GPU) | 4,472 (repeat 0, folds 1–2) | 2,236 (fold 0) |
| B1 | Refit in notebook 06 on CPU, same rows | as B0 | as B0 |
| B2 (primary) | Refit in notebook 06 on CPU without the arXiv pilot rows | B0 fit rows minus pilot | B0 stop rows minus pilot |

B1 separates the effect of refitting from the effect of removing the pilot. B2 contains no publication later than 2024 and only OpenAlex field labels. The refits use float32 on CPU without mixed precision, so they are new fits and not bitwise copies of B0.

**Correction and controls.** For each base, V1–V4 and C1–C3 of step 1 are fitted with the step-1 procedure on the stop rows of that base. The retrieval index for fitting and for evaluation is the fit rows of that base, so the base and the correction see the same labelled publications. Defaults stay k = 5, T = 0.07, ε = 1e−7.

**Limitation fixed in advance.** The stop rows also selected the early-stopping epoch of the paths, so base posteriors on them are slightly optimistic.

**Primary family.** Base B2, endpoint NLL, eight comparisons: cohorts {temporal, external} × variants {V1, V4} × comparators {V0, C1}.
- Paired document bootstrap, B = 20,000, seed 20261105; two-sided bootstrap p-values; Holm correction over the eight comparisons at α = 0.05.
- Δ > 0 favours the corrected variant.
- **Rule.** The correction is supported for a variant on a cohort if both comparisons favour it after adjustment and the lower 95% bound of ΔMacro-F1 against V0 is at least −0.003.

**Descriptive analyses.**
- Metrics of V0–V4 and C1–C3 on both cohorts for B2.
- ΔNLL (V0 − V1) for B0, B1 and B2, and for the recorded configuration (mean development coefficients, index of all 6,708 development rows).
- ΔNLL by quintile of nearest-neighbour similarity within each cohort, and below or above the fixed development threshold 0.757 (the lowest-quintile boundary of step 1).
- ΔNLL by neighbour label agreement: the largest neighbour-class weight below 0.60, from 0.60 to below 1, and equal to 1.
- Per-class recall and ΔNLL.
- Development check with an equal-blend base built from saved artifacts (inner OOF: mean of the saved core and interaction posteriors; outer: saved Dual-Path posteriors): ΔNLL of V1 and V4 against that base and against C1.

## P. Raw-text perturbations

- **Cohort and system.** Temporal cohort, base B2 with V0, V1, V4 and C1. Queries are perturbed; the models and the index are unchanged.
- **Encoders.** Qwen3-Embedding-0.6B and SPECTER2 base with its classification adapter, at the revisions recorded in notebook 02, float32 on this machine. Inputs follow notebook 02: instruction prefix + title + space + abstract for Qwen3; title + separator token + abstract for SPECTER2; at most 512 tokens.
- **Conditions.** Clean (re-encoded); title only; abstract cut to its first 50% of words; abstract cut to its first 25% of words; random deletion of 10% of words; random deletion of 30% of words. Deletion acts on whitespace-separated words of title and abstract, keeps at least one word per field, and uses seed 20261105.
- **Encoder check.** For clean texts, the cosine between fresh and stored embeddings is reported per encoder. The pipeline is accepted if the mean cosine is at least 0.999 for both encoders. If it is not, the results are reported with the re-encoded clean condition as the reference and flagged.
- **Reporting.** Macro-F1, NLL and ECE per condition and variant; ΔNLL (V0 − V1) and (V0 − V4) with 95% bootstrap intervals. Descriptive.
- The external cohort is not perturbed.

## C. Computational cost

For the system B2 + correction on this machine (Apple M1 Pro, 16 GB; encoders on the Apple GPU, heads and retrieval on CPU):
- parameter counts: frozen encoders, trainable base, correction;
- fitting time of the base and of the correction;
- inference time per stage on the temporal cohort: each encoder, base, exact retrieval, correction; total per publication.

Encoding is timed once on the clean condition; the other stages are timed as the median of five repetitions. Descriptive; these values are not comparable with the earlier GPU measurements.

## Deviations recorded during step 2

| Date | Item | Deviation | Handling |
|---|---|---|---|
| 2026-11-10 | Encoding | The first encoding attempt stopped with an out-of-memory error of the Apple GPU backend after 6% of the texts. | Batches are padded to multiples of 64 tokens and the backend cache is released after each batch. Results are unaffected; the encoder check is met (mean cosine 0.99991 and 0.99999). The notebook was then run again from a restarted kernel. |
| 2026-11-10 | Encoder implementation | Qwen3 is run with the base transformer library and last-token pooling. The SPECTER2 classification adapter is applied through forward hooks with the stored adapter weights. Notebook 02 used two wrapper libraries for these steps. | Accepted by the predeclared encoder check. |
| 2026-11-10 | Table 6.10 | The fitted scalar parameters of each base were added to the table after the first pass. | Display only; no analysis changed. |

---

# Step 3 of run rev01: topic-level relevance of neighbours and prespecified confirmation on a newly acquired cohort

Written on 2026-11-10 (13:14 UTC), after steps 1 and 2 were executed and before any step-3 computation or data acquisition. Executed as additional sections of `notebooks/06_revision_ablations_and_corrected_evaluation.ipynb`.

## Purpose

Two points of the review remained open after steps 1 and 2. (i) Retrieval relevance was defined by agreement in the eight broad classes, which measures class consistency and not relevance to a specific topic. (ii) The development gain in NLL was found on a reused panel and had no independent confirmation with a fixed system. Step 3 addresses both.

## T. Topic-level relevance of the retrieved neighbours (descriptive)

- **Question.** Do the neighbours retrieved with the frozen similarity share the topic of the query at finer levels than the eight classes, and are they related to it by citations?
- **Data.** The 5,532 OpenAlex publications of the development panel. Their stored acquisition records (July 2026) contain the primary topic with its subfield and field, and the list of referenced works. The 1,176 arXiv pilot publications carry no OpenAlex topic and are excluded from queries and index.
- **Retrieval.** As in RQ4: queries are the outer-held publications of a context, the index contains its outer-training publications, the similarity is the frozen dual-view cosine, Qwen3 only or SPECTER2 only, and the cutoff is 10.
- **Relevance criteria.** A retrieved publication is relevant if it has (L1) the same field as the query, which is the thematic class; (L2) the same subfield; (L3) the same primary topic; (BC) at least one referenced work in common with the query (bibliographic coupling), evaluated for queries and index publications with at least one recorded reference. A graded criterion assigns gain 3 for the same topic, 2 for the same subfield, 1 for the same field and 0 otherwise.
- **Measures.** Precision@10 and nDCG@10, where the ideal ranking is computed from the index of each query. Queries without any relevant index publication are excluded for that criterion, and their share is reported. Two chance references are reported for Precision@10: a random index publication, and a random index publication of the same class as the query. Mean ± SD over the six outer contexts. No statistical test.
- **Limitation fixed in advance.** OpenAlex topics are assigned automatically from titles, abstracts, sources and citations. The analysis uses no expert judgment of relevance; bibliographic coupling is the only criterion that does not depend on the topic classifier.

## N. Prespecified confirmation on a newly acquired cohort

- **Claim under test.** For publications from the same source, years and eligibility rules as the fit rows, the neighbour correction lowers NLL relative to the base posterior and relative to temperature scaling.
- **Frozen system.** Base B2 and its variants V1 (class-wise coefficients with the multiplier), V4 (one shared coefficient) and C1 (temperature scaling) exactly as fitted in step 2: 3,704 fit rows, 1,828 stop rows, retrieval index of the fit rows, k = 5, T = 0.07, ε = 1e−7. Nothing is refitted or re-selected. The system is written to `results/models/rev01/frozen_system_b2.pt` and its SHA-256 is recorded in `Configs/rev01_experiment.yaml` and below before any record of the new cohort is requested. The evaluation loads this file and verifies the hash. The step-2 values of the temporal cohort (NLL 0.659680 for V0 and 0.658327 for V1) must be reproduced by the loaded system.
- **Registration.** The frozen system was written on 2026-11-10 at 13:25:50 UTC. SHA-256 of the file: `c5adf21f83d0829e8aa731558e8b69bb538e1fa9b869814b7154e8e32f564ef6`. Registered here and in the configuration on 2026-11-10 13:26:19 UTC, before the first request for the new cohort.
- **Cohort.** OpenAlex Works service with the filter of the development acquisition: primary-topic field of the class, abstract available, English, publication date from 2018-01-01 to 2024-12-31; random sample of 200 per request. Three seeds that were never used before are requested for each class: 20269024, 20276943 and 20284862 (24 requests, 4,800 records). Only the fields needed for eligibility, text, labels and references are requested.
- **Eligibility (rules of notebook 02).** Work type article; label equal to the requested class; at least 4 title tokens and 30 abstract tokens; no junk title. Exact duplicates (DOI, normalised title, abstract hash, identifier) and near-duplicates (character TF–IDF cosine of titles of at least 0.94) are resolved within the cohort as in notebook 02. A new record that matches any of the 9,803 corpus publications by one of these keys is removed. No other exclusion is applied. All remaining publications form the cohort, and its size is not adjusted after acquisition.
- **Encoding.** Titles and abstracts are cleaned with the rules of notebook 02 and encoded with the step-2 encoders.
- **Primary family.** Four comparisons on NLL: variants {V1, V4} × comparators {V0, C1}. Paired document bootstrap, B = 20,000, seed 20261105, two-sided bootstrap p-values, Holm correction over the four comparisons at α = 0.05. Δ > 0 favours the corrected variant.
- **Decision rule.** The claim is confirmed for a variant if both of its comparisons favour it after adjustment and the lower 95 % bound of ΔMacro-F1 against V0 is at least −0.003. If the rule fails for both variants, the manuscript states that the development gain was not confirmed on new publications.
- **Single execution.** The evaluation is executed once. It is not repeated with other seeds, sample sizes or settings. Any deviation is recorded below.
- **Descriptive analyses.** Metrics of V0, V1, V4 and C1; ΔNLL of V1 and V4 for bases B0 and B1; ΔNLL by quintile of nearest-neighbour similarity and below or above the fixed threshold 0.757; ΔNLL by class.
- **Label stability (descriptive).** The cohort labels reflect the November 2026 state of OpenAlex, whereas the fit labels were acquired in July 2026. The current primary-topic field of the 5,532 development OpenAlex publications is therefore requested on the acquisition day, and the share of unchanged labels is reported.
- **Limits fixed in advance.** The cohort is a new sample from the service that supplied the fit rows. It tests the in-distribution claim only and says nothing about transfer to other years or sources, which steps 1 and 2 already examined. Labels are assigned automatically. The stop rows of the frozen system also selected the early-stopping epoch of its paths. With about 2,500 publications, the expected half-width of the 95 % interval of ΔNLL is about 0.005 (it was 0.0057 with 1,914 temporal publications), so a difference of the development size (+0.010) can be detected and a much smaller one cannot.

## Deviations recorded during step 3

| Date | Item | Deviation | Handling |
|---|---|---|---|
| 2026-11-10 | Label stability | After Table 6.29 showed that 32.72 % of the development labels have changed in OpenAlex, a breakdown of the cross-validated development predictions by current label state was added (Table 6.30). | Post hoc and descriptive. It uses no publication of the confirmation cohort and does not alter the primary family. |
| 2026-11-10 | Execution | The step-3 cells were first executed one by one in the kernel that held the step-2 state, in the order of the notebook; the system was stored, its hash was registered, and only then were the records requested and the primary family computed. The whole notebook was then executed again from a restarted kernel with the stored responses, embeddings and system. | The primary family was not changed between the two executions; the second execution is the saved record. |
