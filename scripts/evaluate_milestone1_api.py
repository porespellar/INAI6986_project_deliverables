#!/usr/bin/env python3
"""Evaluate local OpenAI-compatible ALPHIN candidates on one locked split."""
from __future__ import annotations

import re
from statistics import median
from typing import Any

WORD = re.compile(r"[a-z0-9]+")
NUMBER_WORDS = {
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
    "nineteen", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
    "hundred", "thousand", "million",
}


def build_prompt(question: str, context: str | None, source_url: str, page: int | str) -> str:
    instructions = (
        "Answer the question concisely. Do not invent facts. If you cannot support the answer, say so. "
        "When you answer, include the supporting source URL and page."
    )
    if context is None:
        return f"{instructions}\n\nQuestion: {question}"
    return (
        f"{instructions}\n\nUse only this supplied source context:\n"
        f"Source: {source_url}, page {page}\n{context}\n\nQuestion: {question}"
    )


def _tokens(text: str) -> list[str]:
    return WORD.findall(text.lower())


def _numeric_tokens(text: str) -> set[str]:
    return {token for token in _tokens(text) if token.isdigit() or token in NUMBER_WORDS}


def score_response(item: dict[str, Any], generated: str) -> dict[str, Any]:
    reference_tokens = set(_tokens(str(item["answer"])))
    generated_tokens = set(_tokens(generated))
    reference_word_recall = len(reference_tokens & generated_tokens) / max(1, len(reference_tokens))
    reference_numbers = _numeric_tokens(str(item["answer"]))
    numeric_token_recall = (
        len(reference_numbers & generated_tokens) / len(reference_numbers) if reference_numbers else 1.0
    )
    source_url = str(item.get("source_url", ""))
    page = str(item.get("page", ""))
    citation_url_present = bool(source_url and source_url in generated)
    citation_page_present = bool(page and re.search(rf"(?:p(?:age)?\.?\s*){re.escape(page)}\b", generated, re.I))
    factual_alignment_pass = reference_word_recall >= 0.60 and numeric_token_recall == 1.0
    citation_present = citation_url_present and citation_page_present
    return {
        "reference_word_recall": round(reference_word_recall, 6),
        "numeric_token_recall": round(numeric_token_recall, 6),
        "citation_url_present": citation_url_present,
        "citation_page_present": citation_page_present,
        "citation_present": citation_present,
        "factual_alignment_pass": factual_alignment_pass,
        "strict_grounded_pass": factual_alignment_pass and citation_present,
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [float(row["latency_seconds"]) for row in rows if row.get("latency_seconds") is not None]
    count = max(1, len(rows))
    return {
        "records": len(rows),
        "factual_alignment_rate": round(sum(bool(row.get("factual_alignment_pass")) for row in rows) / count, 6),
        "citation_rate": round(sum(bool(row.get("citation_present")) for row in rows) / count, 6),
        "strict_grounded_rate": round(sum(bool(row.get("strict_grounded_pass")) for row in rows) / count, 6),
        "mean_reference_word_recall": round(sum(float(row.get("reference_word_recall", 0.0)) for row in rows) / count, 6),
        "median_latency_seconds": round(median(latencies), 6) if latencies else None,
    }
