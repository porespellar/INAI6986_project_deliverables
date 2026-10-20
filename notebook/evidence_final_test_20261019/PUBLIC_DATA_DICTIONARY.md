# Public final-test replay bundle

This scrubbed bundle supports arithmetic replay of the October 19 final-test report. It contains 600 de-identified final-rating rows; paired rows use newly randomized `pair_id` values.

Included are final adjudicated rating dimensions, each judge’s strict-pass bit, a judge-disagreement indicator, the author’s A/B/consensus choice, broad subgroups, the mechanical citation result, latency and token counts.

Excluded are question text, reference answers, evidence quotes, source/page identifiers, passages, model answer text, raw judge prompts/responses, raw model outputs, the benchmark key, private hashes, the signed review spreadsheet, reviewer initials and review timestamps. This bundle reproduces aggregate arithmetic, not semantic judging or source-level validation. The private repository retains the full audit trail.
