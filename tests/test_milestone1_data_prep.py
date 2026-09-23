import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from milestone1_data_prep import curate_file, main, prepare_records, split_name, summarize_records


def test_split_name_matches_document_hash_policy():
    document_id = "doc-1"
    bucket = int(hashlib.sha256(document_id.encode("utf-8")).hexdigest()[:2], 16) % 10
    expected = "test" if bucket == 0 else "validation" if bucket == 1 else "train"
    assert split_name(document_id) == expected


def test_prepare_records_quarantines_blank_unanswerable_and_preserves_others():
    records = [
        {
            "prompt_id": "blank",
            "document_id": "doc-a",
            "unanswerable": True,
            "question": "What is on this blank page?",
            "answer": "",
        },
        {
            "prompt_id": "answerable",
            "document_id": "doc-b",
            "unanswerable": False,
            "question": "What is required?",
            "answer": "A source-supported answer.",
        },
    ]

    approved, quarantined = prepare_records(records)

    assert [r["prompt_id"] for r in approved] == ["answerable"]
    assert approved[0]["split"] == split_name("doc-b")
    assert quarantined == [
        {
            "prompt_id": "blank",
            "reason": "blank_answer_on_unanswerable_source_page",
        }
    ]


def test_prepare_records_rejects_duplicate_prompt_ids():
    records = [
        {"prompt_id": "same", "document_id": "doc-a", "unanswerable": False, "answer": "a"},
        {"prompt_id": "same", "document_id": "doc-b", "unanswerable": False, "answer": "b"},
    ]

    try:
        prepare_records(records)
    except ValueError as exc:
        assert "duplicate prompt_id" in str(exc)
    else:
        raise AssertionError("duplicate prompt IDs must fail closed")


def test_summarize_records_reports_splits_and_no_document_leakage():
    records = [
        {
            "prompt_id": "p1",
            "document_id": "doc-a",
            "split": split_name("doc-a"),
            "answer": "one two three",
            "generator_model": "muse-a",
        },
        {
            "prompt_id": "p2",
            "document_id": "doc-a",
            "split": split_name("doc-a"),
            "answer": "one two",
            "generator_model": "muse-a",
        },
        {
            "prompt_id": "p3",
            "document_id": "doc-b",
            "split": split_name("doc-b"),
            "answer": "one",
            "generator_model": "muse-b",
        },
    ]

    summary = summarize_records(records)

    assert summary["records"] == 3
    assert sum(summary["split_counts"].values()) == 3
    assert summary["unique_documents"] == 2
    assert summary["document_leakage_count"] == 0
    assert summary["answer_words"] == {"min": 1, "median": 2, "max": 3}
    assert summary["generator_models"] == {"muse-a": 2, "muse-b": 1}


def test_curate_file_writes_approved_quarantine_and_summary(tmp_path):
    import json

    source = tmp_path / "source.jsonl"
    source.write_text(
        "\n".join(
            json.dumps(row)
            for row in [
                {"prompt_id": "blank", "document_id": "doc-a", "unanswerable": True, "answer": ""},
                {
                    "prompt_id": "ok",
                    "document_id": "doc-b",
                    "unanswerable": False,
                    "answer": "supported answer",
                    "generator_model": "muse",
                },
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    approved = tmp_path / "approved.jsonl"
    quarantine = tmp_path / "quarantine.jsonl"
    summary = tmp_path / "summary.json"

    result = curate_file(source, approved, quarantine, summary)

    assert result["records"] == 1
    assert len(approved.read_text(encoding="utf-8").splitlines()) == 1
    assert "blank_answer_on_unanswerable_source_page" in quarantine.read_text(encoding="utf-8")
    assert json.loads(summary.read_text(encoding="utf-8"))["quarantined_records"] == 1


def test_main_runs_top_to_bottom(tmp_path):
    import json

    source = tmp_path / "source.jsonl"
    source.write_text(
        json.dumps(
            {
                "prompt_id": "ok",
                "document_id": "doc-b",
                "unanswerable": False,
                "answer": "supported answer",
                "generator_model": "muse",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "--source",
            str(source),
            "--approved",
            str(tmp_path / "approved.jsonl"),
            "--quarantine",
            str(tmp_path / "quarantine.jsonl"),
            "--summary",
            str(tmp_path / "summary.json"),
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "summary.json").exists()
