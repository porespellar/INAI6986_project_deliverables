#!/usr/bin/env python3
"""Download and verify the 2026-09-14 official Alabama Medicaid PDF snapshot.

The PDFs are intentionally not tracked in this public repository. Some contain
published agency contact details. Downloads stay under data/source/ and are
ignored by Git. Each file is checked against the committed manifest SHA-256.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/source/2026-09-14/source_manifest.jsonl"
SOURCE_ROOT = ROOT / "data/source/2026-09-14"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    rows = [json.loads(line) for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip()]
    failures = []
    for index, row in enumerate(rows, 1):
        relative = Path(row["local_path"])
        destination = ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and sha256(destination) == row["sha256"]:
            print(f"[{index}/{len(rows)}] verified cached {destination.name}")
            continue
        request = urllib.request.Request(row["url"], headers={"User-Agent": "INAI6986-reproducibility/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = response.read()
            actual = hashlib.sha256(payload).hexdigest()
            if actual != row["sha256"]:
                failures.append((relative.as_posix(), f"SHA-256 mismatch: {actual}"))
                continue
            destination.write_bytes(payload)
            print(f"[{index}/{len(rows)}] downloaded and verified {destination.name}")
        except (OSError, urllib.error.URLError) as exc:
            failures.append((relative.as_posix(), str(exc)))
    if failures:
        print("Download/verification failures:", file=sys.stderr)
        for name, error in failures:
            print(f"- {name}: {error}", file=sys.stderr)
        return 1
    print(f"Verified {len(rows)} official source PDFs. Files remain local and untracked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
