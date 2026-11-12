# Milestone 3 Rubric Map — Public Package

**Current design:** Open WebUI v0.12.5, 8-step Pipe; untouched Nemotron base drafts and verifies; threshold defaults to 0.80; low-confidence answers go to human review and high-confidence answers are released. The prior exact-quote auto-clear design is removed.

## Approved adaptation

The instructor approved Open WebUI instead of n8n/Make and allowed the rubric to be adapted to the conversational Medicaid-policy RAG workflow (approval reported by the project owner). The implementation is an explicit Pipe and Action inside stock Open WebUI.

## Criterion-to-evidence map

| Rubric criterion | Public evidence and current status |
|---|---|
| Working end-to-end system (25) | The public workflow export and diagram describe intake → retrieval → evidence gate → base draft → confidence/verification → threshold → release/review → log. Confidence-routing screenshots in `evidence/` show four high-confidence releases, four low-confidence reviews and a no-answer route. **Those Oct. 29 captures predate the switch to base-model drafting**; a current base-draft end-to-end capture is pending, and no comparative accuracy result for the current configuration is claimed. |
| Failure handling & duplicate runs (25) | Exported Pipe/Action sources implement input checks, stop-on-service-error, message-keyed run records and idempotent review actions. The full test suite is in the private repo. Fresh current-design browser captures of bad input and service failure remain pending; the public November 10 video captures are from the superseded design and are not evidence for the current configuration. |
| Human-in-the-loop design (15) | Workflow source/docs specify the 0.80 default, high-confidence release, low-confidence review, not-in-documents route, Approve/Needs correction/Escalate actions and SQLite `/log`. Pending items do not expire; the buttons do not notify staff; the confidence is not calibrated. |
| Integration with the model (15) | `workflow/model-reference.md` identifies the pinned public Nemotron BF16 model/revision; exported Pipe source uses the model outside a notebook. Full serving/installer configuration is in the private repository. |
| Evidence & reproducibility (15) | Public package contains the J.O.-only report, rubric map, workflow docs/source export, diagram, confidence-route screenshots and aggregate-only historical summaries. Root repository includes the public Milestone 1/2 documents and de-identified replay materials. Full deployment, runtime and audit lineage are private. The MP4 page is a placeholder pending recording. |
| Honesty about gaps & communication (5) | Report and this map disclose historical-vs-current evidence, missing current base-draft capture, no current-version accuracy estimate, uncalibrated threshold, no notifications/expiry, editable log and prototype-only scope. |

## Routing contract

1. Validate question length and screen for identifier patterns.
2. Retrieve from both knowledge bases (top 8 passages).
3. Base-model evidence gate returns SUFFICIENT / INSUFFICIENT.
4. Untouched Nemotron drafts a cited answer.
5. Base verifier estimates P(YES) from token probabilities; citation/number failure caps confidence at 40%; verifier outage yields 0 and review routing.
6. At/above the configured 0.80 default, release HIGH_CONFIDENCE/AUTO_RELEASED; below it, route LOW_CONFIDENCE/pending.
7. Human actions: Approve, Needs correction (note required), Escalate (note optional).
8. Store route/review decisions in SQLite. The action buttons record decisions; they do not notify staff.

## Evidence limits

- `evaluation/confidence-threshold-summary.json` summarizes 84 already-judged outputs from the earlier adapter-draft workflow: AUROC 0.753; at 80/90/95% thresholds, 49/36/17 outputs released and 5/0/0 wrong core answers. One judge, reused items; exploratory only, not fresh validation, calibration, or a safety guarantee.
- `evaluation/historical-adapter-workflow-summary.json` contains aggregate results from the earlier 49-item adapter-draft run. Those figures are historical, reused and single-judge; do not attribute them to the current base-draft configuration.
- Raw benchmark questions/keys, generated answers, judge requests/responses and reviewer-identifying details are intentionally excluded from the public repository. Complete protected evidence remains in the private repository.

## Submission format

The course rubric asks for one Milestone 3 PDF, 4–6 narrative pages plus evidence appendix, repository access and a 5–8-minute walkthrough recording, including AI Use Disclosure. The public package links to the [official presentation video on AUM YuJa](https://aum.video.yuja.com/V/Video?v=17743008&node=77494270&a=119925289) and to the J.O.-only MP4 in the `m3-walkthrough-v4` GitHub release; matching SRT and VTT captions are included there.
