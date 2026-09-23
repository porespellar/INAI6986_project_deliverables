#!/usr/bin/env python3
"""Milestone 1 deterministic curation helpers."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any


def split_name(document_id: str) -> str:
    bucket = int(hashlib.sha256(document_id.encode("utf-8")).hexdigest()[:2], 16) % 10
    if bucket == 0:
        return "test"
    if bucket == 1:
        return "validation"
    return "train"


def prepare_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    prompt_ids = [str(record.get("prompt_id", "")) for record in records]
    if len(prompt_ids) != len(set(prompt_ids)):
        raise ValueError("duplicate prompt_id detected")

    approved: list[dict[str, Any]] = []
    quarantined: list[dict[str, str]] = []
    for record in records:
        if bool(record.get("unanswerable")) and not str(record.get("answer", "")).strip():
            quarantined.append(
                {
                    "prompt_id": str(record.get("prompt_id", "")),
                    "reason": "blank_answer_on_unanswerable_source_page",
                }
            )
            continue
        curated = dict(record)
        curated["split"] = split_name(str(record["document_id"]))
        approved.append(curated)
    return approved, quarantined


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    split_counts = Counter(str(record["split"]) for record in records)
    document_splits: dict[str, set[str]] = defaultdict(set)
    for record in records:
        document_splits[str(record["document_id"])].add(str(record["split"]))
    answer_word_counts = [len(str(record.get("answer", "")).split()) for record in records]
    generator_models = Counter(str(record.get("generator_model", "unknown")) for record in records)
    return {
        "records": len(records),
        "split_counts": {name: split_counts.get(name, 0) for name in ("train", "validation", "test")},
        "unique_documents": len(document_splits),
        "document_leakage_count": sum(len(splits) > 1 for splits in document_splits.values()),
        "answer_words": {
            "min": min(answer_word_counts) if answer_word_counts else 0,
            "median": int(median(answer_word_counts)) if answer_word_counts else 0,
            "max": max(answer_word_counts) if answer_word_counts else 0,
        },
        "generator_models": dict(sorted(generator_models.items())),
    }


def curate_file(
    source: Path,
    approved_path: Path,
    quarantine_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    records = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    approved, quarantined = prepare_records(records)
    approved_path.parent.mkdir(parents=True, exist_ok=True)
    approved_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in approved),
        encoding="utf-8",
    )
    quarantine_path.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in quarantined),
        encoding="utf-8",
    )
    summary = summarize_records(approved)
    summary["input_records"] = len(records)
    summary["quarantined_records"] = len(quarantined)
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--approved", type=Path, required=True)
    parser.add_argument("--quarantine", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(argv)
    summary = curate_file(args.source, args.approved, args.quarantine, args.summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
