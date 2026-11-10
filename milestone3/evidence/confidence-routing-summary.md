# Milestone 3 Confidence-Routing Evidence (Public Summary)

This evidence comes from saved-chat demonstrations on Open WebUI v0.12.5 on October 29, 2026. Four high-confidence answers (89–97%) were released; four low-confidence answers (9–59%) were sent to review; one question was routed as not in the documents. The captures show the confidence-routing interface and review controls.

**Version qualification:** these saved-chat demonstrations preceded the separate change from adapter drafting to the untouched Nemotron base. They demonstrate the confidence-routing logic, but are not end-to-end live runs of the current base-draft configuration. No comparative accuracy benchmark for that current configuration is claimed.

- [High-confidence route screenshot](high-confidence-route.png)
- [Low-confidence answer and confidence score](low-confidence-review.png)
- [Review actions](review-actions.png)
- Current workflow design and source: `../workflow/README.md` and the exported Pipe/Action files.
- Threshold retrospective summary: `../evaluation/confidence-threshold-summary.json` (84 previously judged answers from the earlier adapter-draft workflow; one judge; reused items; exploratory only, not calibration or fresh validation).

The public package intentionally excludes individual benchmark questions, reference keys, raw generated answers, raw judge requests/responses, review identities/notes, and the runtime database. The complete protected audit trail and deployable stack are maintained in the private repository.
