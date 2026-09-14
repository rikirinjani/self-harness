#!/usr/bin/env python3
"""Re-validation pipeline — Phase 3

Re-runs flagged benchmarks through the executor and (stub) validator,
then updates the comparison report. Exits non-zero if any benchmark
still has executor/validator diff > 1.5.

Usage:
    python tools/revalidate_benchmarks.py
    python tools/revalidate_benchmarks.py BENCH-C-01 BENCH-C-02
    python tools/revalidate_benchmarks.py --threshold 1.0
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS_RUNNER = ROOT / "benchmarks" / "run.py"
VALIDATOR_COMPARE = ROOT / "validator" / "compare_scores.py"
COMPARISON_REPORT = ROOT / "validator" / "comparisons" / "comparison_report.md"


def load_flagged_ids():
    """Read current comparison report and return benchmarks with diff > 1.5."""
    if not COMPARISON_REPORT.exists():
        print(f"Comparison report not found: {COMPARISON_REPORT}")
        sys.exit(1)
    text = COMPARISON_REPORT.read_text(encoding="utf-8")
    flagged = []
    for line in text.splitlines():
        m = re.match(r"\|\s*(BENCH-[A-Z]-\d+)\s*\|\s*\d+/\d+\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*([\d.]+)\s*", line)
        if m:
            bid, diff = m.groups()
            if float(diff) > 1.5:
                flagged.append(bid)
    return flagged


def run_benchmark(bid):
    """Re-run a single benchmark through the executor."""
    print(f"[exec] Running {bid} ...")
    result = subprocess.run(
        [sys.executable, str(BENCHMARKS_RUNNER), bid],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"  {bid} executor failed:\n{result.stderr}")
        return False
    print(f"  {bid} executor completed.")
    return True


def run_validator():
    """Re-run the validator comparison."""
    print("[validator] Regenerating comparison report ...")
    result = subprocess.run(
        [sys.executable, str(VALIDATOR_COMPARE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"Validator comparison failed:\n{result.stderr}")
        return False
    print("[validator] Comparison report regenerated.")
    return True


def check_threshold(threshold):
    """Return list of benchmarks still above the diff threshold."""
    text = COMPARISON_REPORT.read_text(encoding="utf-8")
    still_flagged = []
    for line in text.splitlines():
        m = re.match(r"\|\s*(BENCH-[A-Z]-\d+)\s*\|\s*\d+/\d+\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*([\d.]+)\s*", line)
        if m:
            bid, diff = m.groups()
            if float(diff) > threshold:
                still_flagged.append((bid, float(diff)))
    return still_flagged


def main():
    parser = argparse.ArgumentParser(description="Re-validate flagged benchmarks")
    parser.add_argument("benchmarks", nargs="*", help="Specific benchmark IDs to re-validate")
    parser.add_argument("--threshold", type=float, default=1.5, help="Diff threshold for failure")
    parser.add_argument("--skip-executor", action="store_true", help="Skip re-running executor; only compare existing responses")
    args = parser.parse_args()

    bids = args.benchmarks or load_flagged_ids()
    if not bids:
        print("No flagged benchmarks to re-validate.")
        sys.exit(0)

    print(f"Re-validating {len(bids)} benchmark(s): {', '.join(bids)}")
    print(f"Threshold: diff > {args.threshold}")
    print()

    if not args.skip_executor:
        ok = True
        for bid in bids:
            if not run_benchmark(bid):
                ok = False
        if not ok:
            print("\nOne or more benchmark executions failed.")
            sys.exit(1)

    # Stub: in a full implementation this would re-invoke GPT for each bid.
    # For now we rely on existing responses in validator/responses/.
    if not run_validator():
        sys.exit(1)

    still_flagged = check_threshold(args.threshold)
    print("\n=== Re-validation result ===")
    print(f"Benchmarks checked: {len(bids)}")
    print(f"Still flagged (diff > {args.threshold}): {len(still_flagged)}")
    for bid, diff in still_flagged:
        print(f"  - {bid}: diff {diff:.2f}")

    if still_flagged:
        print("\nEXIT: failure — gap not closed.")
        sys.exit(1)
    else:
        print("\nEXIT: success — all checked benchmarks within threshold.")
        sys.exit(0)


if __name__ == "__main__":
    main()
