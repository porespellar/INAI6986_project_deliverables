# Current Project State — J.O.

## November 23 follow-up — align model selection with film v4

Section 3 now compares five local-model alternatives across four families, matching the current film’s model-selection scene: untouched Nemotron with search, Nemotron with a LoRA adapter, Gemma with adapter, Ornith with adapter, and Muse with adapter. The commercial-service row is removed from Table 5; the prose distinguishes early development probes from the sealed Nemotron base/adapter comparison. Section 7 retains the separate procurement comparison under the generic label “Cloud-hosted commercial AI agent,” with the existing cost allowance and score unchanged and cloud-cost/vendor-control limitations explicit. No new evaluation, earlier-assignment edit or design change occurred. Appendices A–F and all other report sections are unchanged; the report remains 25 pages with 16 body pages.

## November 23, 2026 — Feedback-response appendix added

The current `_v2_Resubmission_1` DOCX/PDF pair now includes **Appendix F · Response to Instructor Feedback**: nine numbered responses with section/table references, correction rationale and explicit unresolved evidence requirements, followed by a request for reassessment. Total: 25 PDF pages, still 16 body pages; Appendix F is printed pages 21–23 (PDF pages 23–25). Cover date, contents and AI disclosure are updated. Report body, Appendices A–D, earlier assignments, code, ratings and evidence inputs are unchanged. No new experimental or human validation was performed. The prior edition remains in Git history; no Canvas submission is claimed.

## November 22, 2026 — Assignment 7A v2 Resubmission 1

Current report: [PDF](docs/J_O_INAI6986_FinalReport_v2_Resubmission_1.pdf) · [DOCX](docs/J_O_INAI6986_FinalReport_v2_Resubmission_1.docx). See the [revision package and financial replay](final_report_v2_Resubmission_1/README.md). 22 pages, including 16 body pages.

The report corrects pass-versus-decline terminology, describes actual shipped behavior and qualifies model-only evidence, CPMAI status, review safeguards and conditional economics. No code, earlier assignment, notebook or recorded rating changed. No new system test or human score was performed. Full-workflow accuracy remains unknown; the candidate and conditional plan are retained, with operational release and procurement on hold. Private benchmark contents remain unpublished. Older status below is historical.


Updated November 12, 2026. Resume with the [public Milestone 3 package](milestone3/README.md) and [current handoff](docs/handoff/HANDOFF_20261110.md); [October 20 handoff](docs/handoff/HANDOFF_20261020.md) is historical.

## November 12 Weekly Progress Deck

A 10-slide J.O.-only progress briefing for Nov 5–12 is in [`presentations/2026-11-12/`](presentations/2026-11-12/) (PPTX and PDF). It summarizes the published walkthrough video, the final Milestone 3 report and Progress Log 3, and the drafted Implementation & Governance Plan (due Nov 22). The plan itself and its builder remain in the private source-of-record repository until submission.

## Milestone 3 In Progress

The public grading package is in [`milestone3/`](milestone3/README.md): J.O.-only Milestone 3 report and Assignment 2C Progress Log 3, rubric map, workflow source/documentation, diagrams, the updated dark-mode main-screen screenshot, confidence-routing evidence, aggregate results and official walkthrough links. The one-page Progress Log covers Weeks 9–12 and includes documented work through Nov 12; its hours field records the student-reported 6 hours this week (Nov 9–15, post-period) and 4 hours last week (Nov 2–8, Week 12; 10 hours across those two weeks); hours for Weeks 9–11 were not provided, so the full-period total is unknown. The [official AUM YuJa presentation](https://aum.video.yuja.com/V/Video?v=17743008&node=77494270&a=119925289) is primary, but anonymous access is unverified; use the alternate [J.O.-only walkthrough MP4](https://github.com/porespellar/INAI6986_project_deliverables/releases/download/m3-walkthrough-v4/INAI6986_M3_Walkthrough_JO_Fall2026.mp4) if AUM sign-in is required. The public release includes captions.

The next phase is a conversational decision-support prototype using stock Open WebUI, Docling, Ollama and Nomic embeddings. The instructor-approved adaptation uses conversational retrieval and human citation review rather than requiring a separate workflow engine. Implementation and complete deployment configuration remain in the private source-of-record repository. This public repository provides the report and most evidence needed for grading review, not a standalone installation.

The refreshed source snapshot is available at `data/source/2026-10-20/`: 138 PDFs with inventory and checksum manifest. Use its updated Administrative Code chapters 13 and 19 for the new knowledge bases and disclose the difference from the September 14 Milestone 2 corpus. Preserve prior snapshots.

The private deployment includes a working Open WebUI/Chroma retrieval workflow and a confidence-routing Pipe. The current base-draft walkthrough is published and demonstrates live workflow paths; comparative accuracy of the current design remains unmeasured. The report's page-one screenshot is updated to show the branded dark-mode main screen and its suggested prompts. No production or agency-use claim is made.

## Milestone 2 Closed

Submitted deliverables and the de-identified final-test arithmetic replay remain unchanged. The fine-tuned adapter was not promoted. Do not rerun or tune against the completed sealed final benchmark. Public replay validates arithmetic from de-identified ratings; it cannot independently reassess source support or semantic answer correctness.

No credentials, runtime databases, private review sheets, model weights or private handoff details are published here.
