# Historical Adapter-Draft Comparison — Public Summary

**Date:** October 29, 2026. **Configuration:** the earlier Pipe that drafted with the adapter. These are historical results, not measurements of the current untouched-base-draft confidence workflow.

## Method and limits

- 49 Administrative Code questions reused from the Milestone 2 benchmark: 40 answerable, 9 unanswerable. Question text only was sent to the models; no passage or reference answer was supplied to generation.
- Single generation per item; one blinded Claude Sonnet 5.5 judge; no human scoring. This is indicative, not a sealed or held-out comparison. Reuse means the 49 items are no longer clean held-out data.
- “Strict pass” requires a correct answer with every claim supported by the short Milestone 2 reference quotes. Retrieval responses may include true additional details that the short quote does not capture; unsupported-detail counts can overstate hallucination.

| Earlier configuration | Answerable correct | Strict pass | Unanswerable declined | Unsupported-claim outputs | Correct in-text citations | Median seconds |
|---|---:|---:|---:|---:|---:|---:|
| Adapter + KBs (Legacy, no workflow) | 30/40 | 28/40 | 2/9 | 19/49 | 6/40 | 30.5 |
| ALPHIN Pipe (adapter draft) | 33/40 | 26/40 | 3/9 | 16/49 | 34/37 answered | 8.4 |

The earlier Pipe did **not** improve strict accuracy (26/40 versus 28/40). Its benefits in that historical run were workflow visibility, citation presence, latency, and a decline/flag route. These figures must not be attributed to the current base-draft design. Aggregate values are reproduced in the submitted Milestone 3 report; the public package does not include question-level keys or raw generated answers.

The confidence-threshold retrospective is a separate one-judge analysis of 84 already-judged answers from this earlier adapter configuration. It is exploratory, uses reused items, and does not establish calibration or safety for the current model configuration.
