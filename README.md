# INAI 6986 — Public Project Deliverables

This repository contains identity-protected public copies of Milestone 1 deliverables and selected supporting code/evidence: reports, the 30-record student-authored independent control set, a reproducibility notebook, pipeline/evaluation code, and reproducibility evidence. The full-name course-submission copies are kept outside this public repository. The public bundle's notebook reruns 11 focused tests; it does not claim to include the complete private-source test suite.

The author is identified as **J.O.** only. No full personal name, private credentials, API keys, or local account paths are intentionally published. The candidate-data copy replaces local generation endpoint identifiers with redacted values. The official source PDFs are **not committed** because the documents may include published agency contact details; the manifest lists official URLs and fingerprints, and the downloader stores verified copies locally under a Git-ignored directory. A few source-derived records may likewise quote generic public Alabama Medicaid contact addresses or service numbers; these are official program contacts, not private individual contact details.

## Deliverables

- `docs/J_O_INAI6986_Milestone2_Current_Development_Report_20261008.pdf` and `.docx` — **current development-phase report, October 8, 2026** (identity-protected; personally reviewed against the Milestone 2 rubric). Reports the completed 192-slot four-family development comparison under the corrected v2 advisory scoring (Nemotron 4/24 base and adapter; Gemma 0→4; Ornith 1→4; Muse 0/24 with a disclosed native-format defect) and the withdrawn-v1 refusal-inflation lesson. **Development evidence only: the protected final benchmark has not been run, final human adjudication is pending, and no final accuracy, threshold verdict, or grade claim is made.**
- `docs/J_O_INAI6986_Milestone1_Resubmission_20261008.pdf` and `.docx` — current Milestone 1 resubmission draft (6 pages: reviewed core plus appendices), October 8, 2026; the sixteen cross-split duplicate groups (57 records) are now human-dispositioned per the submitted Batch A receipt, and the nine unsupported-case items are disclosed as student-adopted AI-assisted drafts rather than independent student authorship. Resubmission is pending instructor acceptance; no grade claim.
- `docs/J_O_INAI6986_Milestone1_v4.pdf` and `.docx` — identity-protected update through October 1, 2026, superseded on October 8 by the resubmission draft above. It adds the eight corrected Nemotron/Ornith nested training runs to the eight Gemma/Muse runs and separates token-level fit from factual-answer performance.
- `docs/J_O_INAI6986_Milestone2.pdf` and `.docx` — October 1 **pre-test working draft, superseded** on October 8 by the current development report above; retained for provenance. No missing score was fabricated in either document.
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

The public bundle intentionally excludes model weights, raw training examples, and the detailed per-run architecture matrix. Full run configurations, token-level metrics, artifact-integrity manifests, and operational records are maintained in the private project repository.
