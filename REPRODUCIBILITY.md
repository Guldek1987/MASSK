# Reproduction scope

This release preserves the executed notebook record and the numerical evidence that accompanies it. The notebook code and saved outputs define the recorded experiments. The YAML files are human-readable descriptions of those experiments, not replacement implementations or settings injected into the notebooks.

## What is available

- Six source notebooks with their saved outputs and figures, copied without changes to code, outputs or explanatory cells. File and cell-source hashes are recorded in [notebook_manifest.csv](provenance/notebook_manifest.csv).
- Public metadata and identifiers for 9,803 retained publications. `publication_id` is the notebook `sample_id`; IDs are not reassigned during packaging.
- Historical train/validation/temporal/external roles, and original outer and inner development fold assignments. Anonymous author–institution proxy groups preserve the grouping used by validation; they are different from exact-duplicate and near-duplicate groups.
- All 19 final development configurations, temporal/external model metrics and paired intervals, and per-class results.
- The 48 development-fitted class coefficients, their eight means used by the stress implementation, and the complete stress model-fit audit.
- Phase-specific experiment descriptions, result-source hashes and recorded software versions.
- Run `rev01` (Notebook 06): the [protocol](docs/research_protocol_rev01.md) written before execution, the [settings](configs/rev01_experiment.yaml), the [recorded environment](configs/rev01_environment.yaml), the result tables of Notebook 06 and its findings table (CSV and LaTeX), the data behind five figures, the figures (PNG and PDF), the [identifiers of the confirmation cohort](data_manifest/confirmation_cohort_ids.csv), and a [result registry](results/tables/rev01/result_registry.csv) that links every table and figure to its notebook section.

Public result files rename display labels and organize saved values; they are not a new model run. Existing point estimates are preserved. The model-specific stress confidence intervals are exported from the recorded interval table, alongside the already published paired intervals.

## Authoritative implementations

| Stage | Implementation and scope |
|---|---|
| Acquisition and preparation | Notebooks 01–02: acquisition, eligibility, text normalization, deduplication, features and initial cohort roles |
| Initial comparator evaluation | Notebook 03: fixed train/validation experiment and comparator settings |
| Final development comparison | Notebook 04: 6,708 pooled development publications; two repeats of three outer folds; inner group cross-fitting; development PRISM-Evidence and eight-coefficient MASSK residual |
| Retrospective stress and raw-text timing | Notebook 05: separately fitted frozen stress model; temporal/external outputs; raw-text benchmark and audit of the distinct runtime processes |
| Revision analyses (run `rev01`) | Notebook 06: variants V0–V5 and controls C1–C3 fitted on identical inner-OOF rows; stress bases B0–B2 built with one specification; raw-text perturbations of the temporal cohort; cost on the Notebook 06 machine; topic-level relevance of neighbours; prespecified confirmation of the frozen system on a newly acquired cohort |

Notebook 04 retains intermediate/rejected architectures as well as the final class-wise residual. The final residual section uses initial γ=0.15, full-batch Adam, learning rate 0.05, exactly 300 iterations, and the best observed fitting objective. The penalty is `0.01 * mean(gamma ** 2)`; for eight classes this equals `0.00125 * sum(gamma ** 2)`. Replacing this with `0.01 * sum(gamma ** 2)`, changing the initialization, or adding patience-based stopping changes the recorded training procedure.

The residual uses `1 - max(p_base)`; margin uncertainty used for risk diagnostics is `1 - (p_top1 - p_top2)`. These quantities serve different purposes. The final class posterior is the softmax of the corrected logits.

The development evidence-only PRISM router has six parameters. The separate retrospective fit tested a 22-parameter router including class priors; all three activation gates failed, leaving the exact 0.5 path blend with temperature 1.0. The same model-family names do not imply identical fitted predictors. Stress γ values are means of the six development coefficient vectors, not coefficients fitted using stress labels.

## Revision run rev01

Notebook 06 was executed from top to bottom after a kernel restart on 10 November 2026: 82 cells, 43 code cells, all executed, no saved error output. The protocol of step 1 is dated 5 November 2026, and the protocols of steps 2 and 3 are dated 10 November 2026. Each was written before the corresponding computations, and the deviations met during execution are listed at the end of each part of the protocol. Steps 1 and 2 are post hoc or retrospective and therefore exploratory; the confirmation of step 3 is the only prespecified test on publications that no earlier analysis had used.

**Reproduction check (Table 6.2).** With the recorded coefficients, Notebook 06 reproduces the recorded Notebook 04 posteriors to within 1.8 × 10⁻⁷. Coefficients refitted on CPU differ from the recorded GPU-fitted coefficients by at most 5.8 × 10⁻⁴. The resulting posteriors exceed the predeclared tolerance of 1 × 10⁻³ in 7 of 13,416 outer-held rows (maximum 1.15 × 10⁻³). The tolerance was not changed and is reported as not met for the refit. The paper-level NLL differs by 2.1 × 10⁻⁶, and the macro-F1 is identical. All variants compared in Notebook 06 use coefficients fitted in that notebook on one device.

**Stress bases.** B0 loads the frozen recorded model. B1 and B2 are new float32 fits on CPU and are not bitwise copies of B0. On the temporal cohort the NLL of B0 and B1 differs by 0.0210 although both use the same rows and settings, so differences of a few thousandths between separately fitted models are within fit-to-fit variation. The stop rows also selected the early-stopping epoch of the paths, so base posteriors on them are slightly optimistic.

**Encoders.** The temporal cohort was re-encoded with Qwen3-Embedding-0.6B and with SPECTER2 base and its classification adapter, at the revisions listed in the settings file. Qwen3 uses the base transformer library with last-token pooling. The SPECTER2 adapter is applied through forward hooks with the stored adapter weights, whereas Notebook 02 used wrapper libraries for both steps. The predeclared check is met: the mean cosine between fresh and stored embeddings of the clean texts is 0.99991 for Qwen3 and 0.99999 for SPECTER2 (Table 6.18).

**Confirmation (step 3).** The evaluated system was stored on 10 November 2026 at 13:25:50 UTC; the SHA-256 of the stored file is `c5adf21f83d0829e8aa731558e8b69bb538e1fa9b869814b7154e8e32f564ef6`. It was registered in the protocol and in the settings at 13:26:19 UTC, and the 24 responses of the OpenAlex service were stored between 13:26:43 and 13:27:31 UTC (Table 6.23). The step-3 cells were first executed one by one in the session that held the step-2 state, in the order of the notebook; the whole notebook was then executed again from a restarted kernel with the stored responses, embeddings and system, and this second execution is the saved record. The primary family (Table 6.27) is identical in both executions, and the base refitted in the saved execution gives the same posteriors as the stored system (Table 6.22). The stored system is not redistributed, in line with the policy for model weights; the identifiers of the 2,940 publications are released. One analysis, the breakdown by label state (Table 6.30), was added after the label-stability result had been seen and is marked as post hoc.

**What a rerun of Notebook 06 needs in addition to this release.** The development and modelling tables with titles and abstracts, the stored embeddings of both encoders, the outer and inner fold tables, the saved inner-OOF and outer posteriors of PRISM-Evidence and of the Dual-Path control, the recorded stress model and its predictions, the stored system of the confirmation, the stored responses of the OpenAlex service for the confirmation cohort and for the label check (or network access to request them again, in which case the service may return different records), and access to the two encoder checkpoints. The exact file names are listed under `inputs` in the settings file. Paths in the notebook follow the original layout (`notebooks/`, `Configs/`, `Docs/`, `dataset/unified/`, `results/tables/`); in this release the first three folders are `Notebooks/`, `configs/` and `docs/`.

## Reading and validating the release

The root `requirements.txt` and `environment.yml` install Jupyter and table-reading utilities for inspection. Open notebooks without executing them to inspect the recorded run. The [notebook manifest](provenance/notebook_manifest.csv) identifies the current notebook bytes; [file checksums](provenance/file_checksums.csv) identify all other release assets. Hash identity confirms file integrity, not independent experimental validation.

The exported fold tables use the original `development_row_index`, `sample_id`, `repeat` and `outer_fold` fields. Inner roles are specific to each outer-training context. A single original train/validation flag is insufficient to reconstruct the final repeated development evaluation. Outer fold seeds were 20267181 and 20268181; stratification used class labels, and grouping used the recorded author–institution proxy.

The source field `arxiv` groups both direct arXiv pilot records and OpenAlex-indexed arXiv records. For `arxiv:W…` IDs, the metadata record and API URL belong to OpenAlex. Where a DOI carries an arXiv accession, `arxiv_url` provides the corresponding landing page. The original stable IDs and labels remain unchanged. The public split name `temporal_test` maps to historical notebook `test`.

On 10 November 2026 the file name of the task specification that the notebooks use to locate the project root was changed in the notebook sources. The change was also applied to the earlier commits of this repository, so their identifiers differ from those issued before that date. No computation and no saved output changed; the file and code-source hashes in the manifests were recomputed, and the output hashes are unchanged. On the same date Notebook 06 and the run `rev01` materials were added as byte-identical copies of the working files, and the manifests were extended accordingly.

## What a fresh execution additionally requires

This compact release does not contain the complete historical runtime workspace. The notebooks retain their original path resolution, absolute paths in some replay cells, references to cached tables/embeddings/model weights, and experiment helper scripts. A clean clone cannot run every cell successfully without restoring those dependencies and adapting only the environment/path setup.

Full re-execution requires:

1. The permitted title/abstract and ancillary source snapshots used by acquisition and preprocessing; current API responses can differ from those historical snapshots.
2. Original aligned feature caches, reference concepts, model checkpoints, intermediate out-of-fold probabilities, experiment helpers and execution receipts referenced by the selected notebook stage, or their regeneration by the corresponding original stages.
3. The original row identities, outer/inner assignments and train-only fitting boundaries. Restoring only cohort flags or recalculating a new split is not an equivalent experiment.
4. The original GPU execution environment and the separate Qwen3 and SPECTER2 adapter processes for the recorded raw-text benchmark.
5. A stage-specific comparison against saved coefficients, probabilities and metrics, with explicitly stated numerical tolerances.

These requirements are disclosed rather than replaced by a newly written trainer. No fresh training or independent full-pipeline reproduction is claimed by this repository update.

## Recorded software environments

[runtime_versions.csv](provenance/runtime_versions.csv) records versions from the saved execution environment and benchmark audit. It is not a complete dependency solver lock and does not establish that every recorded combination is installable from today's package indexes.

The development residual replay records Python 3.12.3, PyTorch 2.12.1+cu130, CUDA 13.0 and an NVIDIA GeForce RTX 5070 Laptop GPU. The raw-text benchmark records Transformers 5.12.1 in its Qwen3 main process and Transformers 4.57.6 with Adapters 1.3.0 in an isolated SPECTER2 worker. Tokenizers 0.22.2 was recorded for both. One generic Transformers pin cannot describe both processes.

Notebook 06 was executed with Python 3.11.15, PyTorch 2.11.0, Transformers 5.7.0 and Requests 2.33.1 on an Apple M1 Pro with 16 GB, with the encoders on the Apple GPU backend and all other stages on CPU in float32. The versions in [rev01_environment.yaml](configs/rev01_environment.yaml) were read from the kernel environment on the day of execution; the notebook itself does not print them.

The saved development replay record allowed differences of at most 0.001 for coefficients/probabilities and 0.000005 for aggregate metrics on the recorded GPU setup. These are historical acceptance tolerances, not a new successful replay. The separate raw-text inference audit retained identical predicted labels with nonzero probability differences (maximum 0.002730); it does not establish bitwise posterior equality or training equivalence.

## Interpretation

Development results are post-selection estimates from a reused panel. The primary classification-superiority criterion failed; secondary NLL/Brier intervals are nominal and post hoc. Temporal and external cohorts had previously exposed label diagnostics and support retrospective stress interpretation only. All temporal paired intervals include zero; external NLL, Brier and ECE deteriorate under the supplied correction. Controlled raw-text perturbations were run only for the temporal cohort in Notebook 06 and are descriptive. Notebook 06 further finds that the development NLL gain exceeds three recalibration controls, that neither the class-specific coefficients nor the confidence multiplier is needed for it, and that the gain does not transfer to either stress cohort when the base and the correction follow one specification. On 2,940 newly acquired publications from the source and years of the fit rows, the prespecified test confirms the gain for the one-coefficient correction and not for the class-wise form with the multiplier.

The original training code and evidence are preserved so these limitations remain inspectable. A later independently implemented model, newly downloaded corpus, alternative runtime, or altered training protocol must be evaluated and reported as its own run.
