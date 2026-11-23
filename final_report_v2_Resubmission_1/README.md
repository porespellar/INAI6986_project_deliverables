# Assignment 7A Final Report — v2 Resubmission 1

Prepared November 22, 2026; updated November 23 with Appendix F, Response to Instructor Feedback. This package adds a report-only revision; earlier assignments, model outputs, ratings, notebooks and system code remain unchanged.

- Report: [`../docs/J_O_INAI6986_FinalReport_v2_Resubmission_1.pdf`](../docs/J_O_INAI6986_FinalReport_v2_Resubmission_1.pdf) and [editable DOCX](../docs/J_O_INAI6986_FinalReport_v2_Resubmission_1.docx).
- 25 PDF pages: cover, contents, 16 body pages, seven appendix pages containing Appendices A–F.
- Appendix F: printed pages 21–23 (PDF pages 23–25). Nine responses identify feedback, exact report locations, rationale and remaining evidence gaps; the closing request seeks reassessment of corrected claims, not credit for tests not performed.
- Author identity: J.O. The full-name submission edition is intentionally outside Git.

The earlier November 23 appendix-only update added the feedback response, updated the cover date, contents and AI-use disclosure, and preserved the report body. The later film-alignment edit changes Sections 3 and 7 only; all appendices remain unchanged. Previous files remain in Git history. Both identity variants passed document/package and pagination checks; only J.O. copies are published.

## November 23 follow-up — align model selection with film v4

Section 3 now compares five local-model alternatives across four families, matching the current film’s model-selection scene: untouched Nemotron with search, Nemotron with a LoRA adapter, Gemma with adapter, Ornith with adapter, and Muse with adapter. The commercial-service row is removed from Table 5; the prose distinguishes early development probes from the sealed Nemotron base/adapter comparison. Section 7 retains the separate procurement comparison under the generic label “Cloud-hosted commercial AI agent,” with the existing cost allowance and score unchanged and cloud-cost/vendor-control limitations explicit. No new evaluation, earlier-assignment edit or design change occurred. Appendices A–F and all other report sections are unchanged; the report remains 25 pages with 16 body pages.

## Corrections and limits

The report separates passage-supplied model scores from unmeasured end-to-end workflow performance; corrects the adapter to one true decline while preserving two recorded passes; describes streaming before confidence scoring, AUTO_RELEASED high-confidence outputs, same-login review, the narrow SSN screen, the 0.80 default and absent durable retry/checkpoint recovery. It distinguishes completed CPMAI work from unmet targets and explains the limits of public arithmetic replay and non-blind human adjudication.

The business case now identifies the chosen 20% unanswerable test mix, assumed review time, unpriced escalation, lack of capacity sizing, and scenario sensitivity. The earlier positive case can reverse with modest incremental escalation work. The candidate design and earlier conditional rollout remain; agency release and procurement are not justified by the existing evidence.

No end-to-end rerun, new blind human score, load test or stakeholder study was performed. Private benchmark questions, reference answers, page locators, outputs and judge rationales are not published in this package. This does not close the semantic-audit gap or guarantee a higher grade.

## Offline financial replay

From the repository root:

```sh
python3 final_report_v2_Resubmission_1/replay_scenarios.py
```

Python standard library only. `cost_inputs.json` contains non-sensitive inputs; `scenario_results.json` contains expected calculations. The script recomputes seven cases and verifies all numeric scenario fields and break-even values. It makes no network calls, runs no model or judge, and does not alter prior evidence.

The original report summed rounded budget lines ($480,374 cost; $568,814 savings; $88,440 net). The saved model used unrounded amounts ($480,372.994013… and $568,814.932), giving $88,441.937987 net. New scenario rows use those unrounded inputs and round once; this is a disclosed rounding convention, not a changed measured result.

The new net figures include −$10,482 if correct declines save no lookup time and −$21,965 if 5% of questions require five additional minutes of escalation. These are hypothetical scenarios, not measured operational results.

## Prior evidence remains historical

The final-test notebook still reproduces stored categorical-rating arithmetic; some historical abstention labels refer to pass counts, not actual refusal behavior. The correction is in this report, not a retrospective alteration of the notebook. The private solution repository holds the historical 100-test workflow suite; the public `tests/` directory contains selected Milestone 1 tests, not that suite.
