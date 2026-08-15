#!/usr/bin/env python3
"""Regenerate data.js from data/*.json + data/index.json for file:// opens."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

def main() -> None:
    index = json.loads((DATA / "index.json").read_text())
    digests = {}
    for path in sorted(DATA.glob("????-??-??.json")):
        digests[path.stem] = json.loads(path.read_text())
    payload = {"index": index, **digests}
    out = (
        "window.DIGEST_INDEX = "
        + json.dumps(index, indent=2)
        + ";\n"
        + "window.DIGESTS = "
        + json.dumps(payload, indent=2)
        + ";\n"
    )
    (ROOT / "data.js").write_text(out)
    print(f"Wrote {ROOT / 'data.js'} ({len(digests)} digests)")

if __name__ == "__main__":
    main()
