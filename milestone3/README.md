# INAI 6986 Milestone 3 — Public Grading and Evidence Package

This J.O.-only package is the public companion to the Milestone 3 submission. It contains the report, rubric map, current workflow export/documentation, diagrams, confidence-routing screenshots, and aggregate evaluation summaries. The repository root also contains the identity-protected public Milestone 1/2 deliverables, public-source artifacts, and existing de-identified replay notebooks.

> Figure 1 on page 1 is a fresh dark-mode Open WebUI home-screen capture with the AUM-orange sidebar, current suggested prompts, and branded background under the 0.40 dark veil. It demonstrates the interface appearance, not an answer run.

## Submission documents

- [Milestone 3 PDF](../docs/J_O_INAI6986_Milestone3_20261110.pdf)
- [Editable Milestone 3 DOCX](../docs/J_O_INAI6986_Milestone3_20261110.docx)
- [Assignment 2C Progress Log 3 PDF](../docs/J_O_INAI6986_Log3_20261110.pdf)
- [Editable Progress Log 3 DOCX](../docs/J_O_INAI6986_Log3_20261110.docx)
- [Rubric map](MILESTONE3_RUBRIC_MAP.md)

> The Progress Log follows the one-page Assignment 2C template and includes documented work through Nov 12. Its hours field records 6 hours this week and 4 hours last week (10 across those two weeks); hours for Weeks 9–11 were not supplied, so the full-period total is unknown.

## Workflow evidence

- [Workflow explanation and rubric-relevant steps](workflow/README.md)
- Exported Pipe: `workflow/alphin_policy_workflow.py`
- Exported Review Action: `workflow/alphin_review_actions.py`
- Public wrapper model configuration: `workflow/alphin-policy-workflow.json` (the public suggestion describes an identifier-check demo without embedding a test identifier); [pinned base-model reference](workflow/model-reference.md)
- [Current confidence-routing evidence note](evidence/confidence-routing-summary.md), the corrected dark-mode main-screen screenshot (`evidence/main-openwebui-dark-sidebar.png`: orange sidebar, visible prompts, background under the 0.40 veil), three confidence/review screenshots, and [path diagrams](workflow/path_examples.png)
- [Exploratory confidence-threshold summary](evaluation/confidence-threshold-summary.json)
- [Historical adapter-draft comparison method](evaluation/historical-adapter-workflow-method.md) and aggregate-only results in `evaluation/historical-adapter-workflow-summary.json`
- [Official presentation video on AUM YuJa](https://aum.video.yuja.com/V/Video?v=17743008&node=77494270&a=119925289) *(anonymous access has not been verified; use the MP4 release if AUM sign-in is required)*
- [Alternate: J.O.-only walkthrough MP4](../videos/INAI6986_Milestone3_Walkthrough.md) and [public GitHub release with captions](https://github.com/porespellar/INAI6986_project_deliverables/releases/tag/m3-walkthrough-v4)

## What this public repository does and does not provide

The public package is sufficient to review the report's rubric mapping, documented workflow, displayed confidence-routing evidence, and aggregate historical results. It is **not** a clone-and-run deployment. The full private repository contains the complete installer/configuration, pinned runtime and model artifacts, test suite, live deployment materials, and the protected source-level audit trail. Base model weights are retrieved from the pinned public model revision; the experimental adapter and runtime databases are not duplicated here.

For evaluation integrity and privacy, this public package excludes held-out question/reference keys, raw answer text and raw judge requests/responses, reviewer identities and notes, runtime databases, credentials, tokens, and personal names. Historical metrics are explicitly separated from the current base-draft workflow; no current-version comparative accuracy claim is made.
