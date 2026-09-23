# INAI 6986 — Public Project Deliverables

This repository contains only the professor-facing Milestone 1 deliverables and the supporting code/evidence needed to inspect the rubric requirements: the final report, the 30-record student-authored independent control set, a reproducibility notebook, selected pipeline/evaluation code, and reproducibility evidence.

The author is identified as **J.O.** only. No full personal name, private credentials, API keys, or local account paths are intentionally published. The candidate-data copy replaces local generation endpoint identifiers with redacted values. The official source PDFs are **not committed** because the documents may include published agency contact details; the manifest lists official URLs and fingerprints, and the downloader stores verified copies locally under a Git-ignored directory. A few source-derived records may likewise quote generic public Alabama Medicaid contact addresses or service numbers; these are official program contacts, not private individual contact details.

## Deliverables

- `docs/INAI6986_Milestone1_v2.pdf` and `.docx` — Milestone 1 report.
- `docs/Student_Authored_Independent_Control_Set_30_Questions.pdf` and `.docx` — completed student-authored control set.
- `docs/Student_Authored_Control_Set_30_Questions.jsonl` — structured control records and source provenance.
- `notebook/milestone1_reproducibility.ipynb` — recomputes data-preparation, split, provenance, leakage, training-status, tests, and diagnostic evaluation summaries. It does not rerun local model training/inference or claim the missing human factual-accuracy scores.
- `scripts/`, `tests/`, `data/`, and `artifacts/` — the selected supporting pipeline, redacted input records, test suite, and evidence snapshots.

## Reproduce the notebook

From the repository root:

```bash
python3 scripts/download_public_sources.py
uv run --with pytest --with nbconvert --with nbformat jupyter nbconvert --to notebook --execute notebook/milestone1_reproducibility.ipynb --output milestone1_reproducibility.executed.ipynb
```

The source downloader verifies SHA-256 for every PDF. PDFs remain local, are ignored by Git, and are not uploaded by the commands above. Review the notebook's open completion gates before treating the diagnostic metrics as a factual-accuracy result. The independent 30-record control set is excluded from training and retained for human scoring.

The submitted report documents the evidence cutoff and known limitations. Public access allows anyone to view and copy repository contents; this repository is not a private access-control mechanism.
