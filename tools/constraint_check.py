#!/usr/bin/env python3
"""Constraint Check Helper — P-001

Parses a plain-text spec and a code/implementation file, then reports which
constraint keywords from the spec appear in the implementation.

Usage:
    python tools/constraint_check.py --spec spec.txt --impl code.py
    python tools/constraint_check.py --spec "must handle empty input; must not add deps" --impl code.py
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def extract_constraints(text):
    """Naive constraint extractor: look for imperative phrases."""
    text = text.lower()
    # Split on sentence terminators and semicolons
    chunks = re.split(r"[.;\n]", text)
    constraints = []
    markers = [
        "must", "should", "need to", "required", "forbidden", "not allowed",
        "must not", "must be", "must handle", "must support", "must return",
        "must use", "must follow", "must pass", "must compile", "no new",
        "edge case", "regression", "existing tests", "style", "format",
    ]
    for chunk in chunks:
        chunk = chunk.strip()
        if any(chunk.startswith(m) or (" " + m in chunk) for m in markers):
            # Drop filler words and normalize
            cleaned = re.sub(r"[^a-z0-9\s_-]", "", chunk)
            if cleaned:
                constraints.append(cleaned)
    return constraints


def check_coverage(constraints, impl_text):
    impl_text = impl_text.lower()
    covered = []
    missing = []
    for c in constraints:
        # Require at least 2 significant words from the constraint to appear
        words = [w for w in c.split() if len(w) > 2]
        if not words:
            missing.append(c)
            continue
        matches = sum(1 for w in words if w in impl_text)
        if matches >= max(1, len(words) // 2):
            covered.append(c)
        else:
            missing.append(c)
    return covered, missing


def main():
    parser = argparse.ArgumentParser(description="Check spec constraint coverage in implementation")
    parser.add_argument("--spec", required=True, help="Path to spec file or inline spec string")
    parser.add_argument("--impl", required=True, help="Path to implementation file")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if spec_path.exists():
        spec_text = spec_path.read_text(encoding="utf-8")
    else:
        spec_text = args.spec

    impl_path = Path(args.impl)
    if not impl_path.exists():
        print(f"Implementation file not found: {impl_path}", file=sys.stderr)
        sys.exit(1)
    impl_text = impl_path.read_text(encoding="utf-8")

    constraints = extract_constraints(spec_text)
    covered, missing = check_coverage(constraints, impl_text)

    result = {
        "spec": str(spec_path) if spec_path.exists() else args.spec,
        "impl": str(impl_path),
        "constraints": constraints,
        "covered": covered,
        "missing": missing,
        "pass": len(missing) == 0,
        "coverage_ratio": round(len(covered) / len(constraints), 2) if constraints else 1.0,
    }

    print(json.dumps(result, indent=2))
    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
