# INAI 6986 — Public Project Deliverables

This repository contains identity-protected public copies of Milestone 1 deliverables and selected supporting code/evidence: reports, the 30-record student-authored independent control set, a reproducibility notebook, pipeline/evaluation code, and reproducibility evidence. The full-name course-submission copies are kept outside this public repository. The public bundle's notebook reruns 11 focused tests; it does not claim to include the complete private-source test suite.

The author is identified as **J.O.** only. No full personal name, private credentials, API keys, or local account paths are intentionally published. The candidate-data copy replaces local generation endpoint identifiers with redacted values. The official source PDFs are **not committed** because the documents may include published agency contact details; the manifest lists official URLs and fingerprints, and the downloader stores verified copies locally under a Git-ignored directory. A few source-derived records may likewise quote generic public Alabama Medicaid contact addresses or service numbers; these are official program contacts, not private individual contact details.

## Current October 18 Package

- `docs/J_O_INAI6986_Milestone1_v5.docx` and `.pdf` — October 18 revised Milestone 1 (8 pages): plain-language rewrite; Wilson 95% intervals and exact paired tests for the 24-question development comparison; the Week 8 human review of the selected candidate; interpretability findings (citation format without grounding, loss of abstention, judge reliability); duplicate-group rulings; response to instructor feedback.
- `docs/J_O_INAI6986_Milestone2_20261018.docx` and `.pdf` — October 18 Milestone 2 (6 pages) in assignment-template order. **All results are development results on validation questions; the one-time final test has not been run.** Development verdict: threshold not met. Adds a declared pre-test protocol change: two LLM judges score the full output set instead of a blind human-rated sample; Qwen + Claude Sonnet 5.5 through the Claude Code CLI / Hermes Direct Claude Code SDK; citation correctness checked mechanically. The report explicitly calls this a trade-off, not equivalent human validation.
- `docs/J_O_INAI6986_Log2_20261018.docx` and `.pdf` — Progress Log 2 (Week 8, October 5–11), one page, seven template fields; hours are an estimate; the next-period tasks now disclose the two-LLM judging plan and no blind human-rating sample.
- `notebook/current_evidence_replay_20261018.ipynb` — executed record (5 code cells, 0 errors) of the replay that recomputes every development number in the October 18 documents. Inputs and the derived results are in `notebook/evidence_20261018/` (`development_analysis_20261018.json` plus the scrubbed per-output bundle). Re-execution needs the private source-of-record repository; a self-contained public version will follow with the final-test notebook.

## October 16 Package (superseded by the October 18 package)

Personally reviewed by GPT-6.1 Sol against the actual assignment rubrics and recorded instructor feedback. These are evidence-bound development drafts, not a claim of completed final evaluation or a guaranteed grade.

- `docs/J_O_INAI6986_Milestone1_v4.docx` and `.pdf` — October 16 feedback-responsive report: five-page core plus appendices, 14 pages total. Preserves the original controls; reconciles completed human dispositions, AI-assisted adopted items, development findings and remaining factual-comparison gaps. This update supersedes the October 1 copy at the same path and the October 8 draft below.
- `docs/J_O_INAI6986_Milestone2.docx` and `.pdf` — October 16 pre-test working report: seven-page core plus evidence/criterion appendices, 10 pages total. Current development metrics are measured; final comparison, final robustness and final subgroup metrics remain NOT RUN. This update supersedes the older copy at the same path, not the historical records themselves.
- `docs/J_O_INAI6986_Log2_20261016.docx` and `.pdf` — standalone Progress Log 2: Week 8, October 5–11; October 16 follow-up separately dated; 20 hours explicitly estimated, not measured; one-page status plus disclosure/evidence addendum.
- `notebook/current_evidence_replay_20261016.ipynb`, `.html`, `.pdf` and `_receipt.json` — five sequential code cells, zero errors in fresh-kernel execution; recomputes current training and development-advisory metrics from the scrubbed per-epoch/per-output records in `notebook/evidence_20261016/`, verifying all six input fingerprints. It is a replay, not new training/inference or the missing final test.

Final source approval, native runtime/matched-model proof, immutable protocol seal and genuinely new human ratings remain open. No protected final campaign or deployment approval is claimed. See `docs/README_sol_review_20261016.md` for exact evidence and limitations.

## Historical Deliverables

- `docs/J_O_INAI6986_Milestone2_Current_Development_Report_20261008.pdf` and `.docx` — **current development-phase report, October 8, 2026** (identity-protected; personally reviewed against the Milestone 2 rubric). Reports the completed 192-slot four-family development comparison under the corrected v2 advisory scoring (Nemotron 4/24 base and adapter; Gemma 0→4; Ornith 1→4; Muse 0/24 with a disclosed native-format defect) and the withdrawn-v1 refusal-inflation lesson. **Development evidence only: the protected final benchmark has not been run, final human adjudication is pending, and no final accuracy, threshold verdict, or grade claim is made.**
- `docs/J_O_INAI6986_Milestone1_Resubmission_20261008.pdf` and `.docx` — current Milestone 1 resubmission draft (6 pages: reviewed core plus appendices), October 8, 2026; the sixteen cross-split duplicate groups (57 records) are now human-dispositioned per the submitted Batch A receipt, and the nine unsupported-case items are disclosed as student-adopted AI-assisted drafts rather than independent student authorship. Resubmission is pending instructor acceptance; no grade claim.
- The October 1 versions of the current Milestone 1 v4 and Milestone 2 paths remain in Git history; their paths now contain the October 16 updates listed above.
- `docs/J_O_INAI6986_Milestone1_v3.pdf` and `.docx` — historical identity-protected post-feedback supplement through September 30, 2026, at 12:34 PM CDT. The historical notebook below does not reproduce later model training.
- `docs/INAI6986_Milestone1_v2.pdf` and `.docx` — identity-protected historical Milestone 1 report, retained unchanged by this publication.
- `docs/Student_Authored_Independent_Control_Set_30_Questions.pdf` and `.docx` — completed student-authored control set.
- `docs/Student_Authored_Control_Set_30_Questions.jsonl` — structured control records and source provenance.
- `notebook/milestone1_reproducibility.ipynb` — archived earlier-phase notebook for the original data and legacy diagnostic workflow; it does not reproduce or contribute metrics to the current matched comparison. Use the current v3 report's Gemma/Muse tables for current training results.
- `scripts/`, `tests/`, and `data/` contain the selected supporting pipeline, redacted inputs and test suite. `artifacts/` also preserves earlier Milestone 1 evidence, including explicitly labeled pre-amendment Muse files; use the v3 report as the authoritative source for current matched-run results.

## Reproduce the notebook

From the repository root:

```bash
python3 scripts/download_public_sources.py
uv run --with pytest --with nbconvert --with nbformat jupyter nbconvert --to notebook --execute notebook/milestone1_reproducibility.ipynb --output milestone1_reproducibility.executed.ipynb
```

The source downloader verifies SHA-256 for every PDF. PDFs remain local, are ignored by Git, and are not uploaded by the commands above. This archived notebook reproduces only the earlier data-preparation/legacy-diagnostic workflow; its historical tables are not current matched-run results. Current Gemma/Muse metrics are in the v3 report. The independent 30-record control set remains excluded from training and unused in the current run matrix.

Each report documents its evidence cutoff and known limitations. Public access allows anyone to view and copy repository contents; this repository is not a private access-control mechanism.

## Detailed training evidence

The public bundle excludes model weights, raw training examples, local endpoints and protected new-benchmark question/key text. The October 16 replay includes only the scrubbed numeric per-epoch/per-output records needed to reproduce its displayed development metrics, plus structural corpus/source-membership audits and their manifest. It does not include raw inference prompts, answer text or native training assets. Full operational records and original-byte provenance remain in the private source repository.
