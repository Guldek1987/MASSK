# Reproduction scope

This release preserves the executed notebook record and the numerical evidence that accompanies it. The notebook code and saved outputs define the recorded experiments. The YAML files are human-readable descriptions of those experiments, not replacement implementations or settings injected into the notebooks.

## What is available

- Five source notebooks with their saved outputs and figures, copied without changes to code, outputs or explanatory cells. File and cell-source hashes are recorded in [notebook_manifest.csv](provenance/notebook_manifest.csv).
- Public metadata and identifiers for 9,803 retained publications. `publication_id` is the notebook `sample_id`; IDs are not reassigned during packaging.
- Historical train/validation/temporal/external roles, and original outer and inner development fold assignments. Anonymous author–institution proxy groups preserve the grouping used by validation; they are different from exact-duplicate and near-duplicate groups.
- All 19 final development configurations, temporal/external model metrics and paired intervals, and per-class results.
- The 48 development-fitted class coefficients, their eight means used by the stress implementation, and the complete stress model-fit audit.
- Phase-specific experiment descriptions, result-source hashes and recorded software versions.

Public result files rename display labels and organize saved values; they are not a new model run. Existing point estimates are preserved. The model-specific stress confidence intervals are exported from the recorded interval table, alongside the already published paired intervals.

## Authoritative implementations

| Stage | Implementation and scope |
|---|---|
| Acquisition and preparation | Notebooks 01–02: acquisition, eligibility, text normalization, deduplication, features and initial cohort roles |
| Initial comparator evaluation | Notebook 03: fixed train/validation experiment and comparator settings |
| Final development comparison | Notebook 04: 6,708 pooled development publications; two repeats of three outer folds; inner group cross-fitting; development PRISM-Evidence and eight-coefficient MASSK residual |
| Retrospective stress and raw-text timing | Notebook 05: separately fitted frozen stress model; temporal/external outputs; raw-text benchmark and audit of the distinct runtime processes |

Notebook 04 retains intermediate/rejected architectures as well as the final class-wise residual. The final residual section uses initial γ=0.15, full-batch Adam, learning rate 0.05, exactly 300 iterations, and the best observed fitting objective. The penalty is `0.01 * mean(gamma ** 2)`; for eight classes this equals `0.00125 * sum(gamma ** 2)`. Replacing this with `0.01 * sum(gamma ** 2)`, changing the initialization, or adding patience-based stopping changes the recorded training procedure.

The residual uses `1 - max(p_base)`; margin uncertainty used for risk diagnostics is `1 - (p_top1 - p_top2)`. These quantities serve different purposes. The final class posterior is the softmax of the corrected logits.

The development evidence-only PRISM router has six parameters. The separate retrospective fit tested a 22-parameter router including class priors; all three activation gates failed, leaving the exact 0.5 path blend with temperature 1.0. The same model-family names do not imply identical fitted predictors. Stress γ values are means of the six development coefficient vectors, not coefficients fitted using stress labels.

## Reading and validating the release

The root `requirements.txt` and `environment.yml` install Jupyter and table-reading utilities for inspection. Open notebooks without executing them to inspect the recorded run. The [notebook manifest](provenance/notebook_manifest.csv) identifies the current notebook bytes; [file checksums](provenance/file_checksums.csv) identify all other release assets. Hash identity confirms file integrity, not independent experimental validation.

The exported fold tables use the original `development_row_index`, `sample_id`, `repeat` and `outer_fold` fields. Inner roles are specific to each outer-training context. A single original train/validation flag is insufficient to reconstruct the final repeated development evaluation. Outer fold seeds were 20267181 and 20268181; stratification used class labels, and grouping used the recorded author–institution proxy.

The source field `arxiv` groups both direct arXiv pilot records and OpenAlex-indexed arXiv records. For `arxiv:W…` IDs, the metadata record and API URL belong to OpenAlex. Where a DOI carries an arXiv accession, `arxiv_url` provides the corresponding landing page. The original stable IDs and labels remain unchanged. The public split name `temporal_test` maps to historical notebook `test`.

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

The saved development replay record allowed differences of at most 0.001 for coefficients/probabilities and 0.000005 for aggregate metrics on the recorded GPU setup. These are historical acceptance tolerances, not a new successful replay. The separate raw-text inference audit retained identical predicted labels with nonzero probability differences (maximum 0.002730); it does not establish bitwise posterior equality or training equivalence.

## Interpretation

Development results are post-selection estimates from a reused panel. The primary classification-superiority criterion failed; secondary NLL/Brier intervals are nominal and post hoc. Temporal and external cohorts had previously exposed label diagnostics and support retrospective stress interpretation only. All temporal paired intervals include zero; external NLL, Brier and ECE deteriorate under the supplied correction. Controlled raw-text perturbation tests were not performed.

The original training code and evidence are preserved so these limitations remain inspectable. A later independently implemented model, newly downloaded corpus, alternative runtime, or altered training protocol must be evaluated and reported as its own run.
