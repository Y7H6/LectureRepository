#!/usr/bin/env python3
"""
scripts/validate_design_doc.py

- Reads spec/design/design_doc_ref.json
- Verifies the design doc exists at the configured path and contains required phrases.
Exit codes:
  0 -> OK
  1 -> spec file missing or unreadable
  2 -> design doc missing
  3 -> content check failed
"""
import json
import sys
from pathlib import Path

SPEC_FILE = Path("spec/design/design_doc_ref.json")

def main():
    if not SPEC_FILE.exists():
        print(f"Spec file not found: {SPEC_FILE}")
        return 1

    try:
        spec = json.loads(SPEC_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read/parse spec file: {e}")
        return 1

    doc_path = Path(spec.get("doc_path", "")).resolve()
    if not doc_path.exists():
        print(f"Design doc not found: {doc_path}")
        return 2

    content = doc_path.read_text(encoding="utf-8")
    missing = []
    for phrase in spec.get("checks", {}).get("must_contain", []):
        if phrase not in content:
            missing.append(phrase)

    if missing:
        print("Design doc is missing required phrases:")
        for m in missing:
            print(" -", m)
        return 3

    print("Design doc exists and passed checks.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
