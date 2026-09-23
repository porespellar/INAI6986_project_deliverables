import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_milestone1_api import build_prompt, score_response, summarize_rows


def test_build_prompt_without_context_requests_grounded_answer_and_citation():
    prompt = build_prompt("What is required?", None, "https://example.test/doc.pdf", 7)
    assert "What is required?" in prompt
    assert "https://example.test/doc.pdf" not in prompt
    assert "source URL and page" in prompt


def test_build_prompt_with_context_includes_only_supplied_source():
    prompt = build_prompt(
        "What is required?",
        "The provider must file within one year.",
        "https://example.test/doc.pdf",
        7,
    )
    assert "The provider must file within one year." in prompt
    assert "https://example.test/doc.pdf" in prompt
    assert "page 7" in prompt


def test_score_response_requires_key_facts_and_tracks_citation():
    item = {
        "answer": "Claims must be filed within one year.",
        "source_url": "https://example.test/doc.pdf",
        "page": 7,
    }
    scored = score_response(
        item,
        "Claims must be filed within one year. Source: https://example.test/doc.pdf page 7.",
    )
    assert scored["reference_word_recall"] == 1.0
    assert scored["numeric_token_recall"] == 1.0
    assert scored["citation_present"] is True
    assert scored["factual_alignment_pass"] is True
    assert scored["strict_grounded_pass"] is True


def test_score_response_fails_when_numeric_fact_is_wrong():
    item = {
        "answer": "Claims must be filed within one year.",
        "source_url": "https://example.test/doc.pdf",
        "page": 7,
    }
    scored = score_response(item, "Claims must be filed within two years.")
    assert scored["numeric_token_recall"] == 0.0
    assert scored["factual_alignment_pass"] is False
    assert scored["strict_grounded_pass"] is False


def test_summarize_rows_computes_declared_metrics():
    rows = [
        {
            "reference_word_recall": 1.0,
            "numeric_token_recall": 1.0,
            "citation_present": True,
            "factual_alignment_pass": True,
            "strict_grounded_pass": True,
            "latency_seconds": 2.0,
        },
        {
            "reference_word_recall": 0.5,
            "numeric_token_recall": 0.0,
            "citation_present": False,
            "factual_alignment_pass": False,
            "strict_grounded_pass": False,
            "latency_seconds": 4.0,
        },
    ]

    summary = summarize_rows(rows)

    assert summary["records"] == 2
    assert summary["factual_alignment_rate"] == 0.5
    assert summary["citation_rate"] == 0.5
    assert summary["strict_grounded_rate"] == 0.5
    assert summary["mean_reference_word_recall"] == 0.75
    assert summary["median_latency_seconds"] == 3.0
