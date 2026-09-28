# INAI 6986 — Public Project Deliverables

This repository contains identity-protected public copies of Milestone 1 deliverables and selected supporting code/evidence: reports, the 30-record student-authored independent control set, a reproducibility notebook, pipeline/evaluation code, and reproducibility evidence. The full-name course-submission copies are kept outside this public repository. The public bundle's notebook reruns 11 focused tests; it does not claim to include the complete private-source test suite.

The author is identified as **J.O.** only. No full personal name, private credentials, API keys, or local account paths are intentionally published. The candidate-data copy replaces local generation endpoint identifiers with redacted values. The official source PDFs are **not committed** because the documents may include published agency contact details; the manifest lists official URLs and fingerprints, and the downloader stores verified copies locally under a Git-ignored directory. A few source-derived records may likewise quote generic public Alabama Medicaid contact addresses or service numbers; these are official program contacts, not private individual contact details.

## Deliverables

- `docs/J_O_INAI6986_Milestone1_v3.pdf` and `.docx` — identity-protected post-feedback supplement; its five-page core and appendices distinguish verified changes from unresolved evaluation gates. New Gemma training results are not reproduced by the historical notebook below.
- `docs/INAI6986_Milestone1_v2.pdf` and `.docx` — identity-protected historical Milestone 1 report, retained unchanged by this publication.
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

Each report documents its evidence cutoff and known limitations. Public access allows anyone to view and copy repository contents; this repository is not a private access-control mechanism.
