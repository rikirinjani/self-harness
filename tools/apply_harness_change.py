#!/usr/bin/env python3
"""Apply Harness Change — Phase 5

Takes an approved proposal, uses harness_architect.py to generate shadow diffs,
optionally runs the validator comparison in shadow mode, and reports whether the
change is likely beneficial.

Usage:
    python tools/apply_harness_change.py P-004
    python tools/apply_harness_change.py proposals/json/P-004.json --benchmarks BENCH-O-04 BENCH-O-05
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
SHADOW_DIR = ROOT / "shadow"
SHADOW_REPORTS = SHADOW_DIR / "reports"


def load_proposal(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_architect(proposal_path, shadow_dir):
    """Invoke harness_architect.py to generate diffs."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "harness_architect.py"), str(proposal_path), "--shadow-dir", str(shadow_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"Architect failed:\n{result.stderr}")
        sys.exit(1)
    return result.stdout


def run_baseline_comparison():
    """Capture current comparison report summary."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "validator" / "compare_scores.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"Baseline comparison failed:\n{result.stderr}")
        sys.exit(1)
    # Extract avg diff from output
    for line in result.stdout.splitlines():
        if "avg diff" in line:
            m = re.search(r"avg diff ([\d.]+)", line)
            if m:
                return float(m.group(1))
    return None


def run_shadow_comparison(benchmarks):
    """Run a limited shadow re-validation using the same validator responses.
    
    In a full implementation this would execute benchmarks under shadow rules.
    For this scaffold we assume the proposal is a process/rule change whose
    immediate effect is not measurable via existing benchmark diffs, so we
    report the baseline as the shadow result and note the limitation.
    """
    # Placeholder: real shadow run would copy outputs, apply shadow rules, and re-score.
    print(f"[shadow] Would re-run benchmarks: {', '.join(benchmarks)}")
    return None


def write_report(proposal, baseline, shadow, output_path):
    """Write shadow-mode report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "proposal_id": proposal.get("proposal_id"),
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "baseline_avg_diff": baseline,
        "shadow_avg_diff": shadow,
        "recommendation": "deploy" if (shadow is not None and shadow <= baseline) else "manual_review",
        "notes": "Shadow scaffold: rule/process proposals do not produce immediate benchmark diffs; measure via long-term failure-rate trend."
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Shadow report: {output_path}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Apply a harness change in shadow mode")
    parser.add_argument("proposal", help="Proposal id (P-NNN) or path to JSON proposal")
    parser.add_argument("--benchmarks", nargs="*", help="Benchmarks to re-validate in shadow")
    parser.add_argument("--shadow-dir", default=str(SHADOW_DIR), help="Shadow harness directory")
    args = parser.parse_args()

    if not args.proposal.endswith(".json"):
        proposal_path = ROOT / "proposals" / "json" / f"{args.proposal}.json"
    else:
        proposal_path = Path(args.proposal)

    proposal = load_proposal(proposal_path)
    shadow_dir = Path(args.shadow_dir)

    print(f"Applying {proposal['proposal_id']} in shadow mode...")
    architect_output = run_architect(proposal_path, shadow_dir)
    print(architect_output)

    baseline = run_baseline_comparison()
    print(f"Baseline avg diff: {baseline}")

    benchmarks = args.benchmarks or proposal.get("verification", {}).get("secondary_benchmarks", [])
    if not benchmarks:
        benchmarks = [proposal.get("verification", {}).get("primary_benchmark", "")]
    shadow = run_shadow_comparison(benchmarks)

    report_path = shadow_dir / "reports" / f"{proposal['proposal_id']}-shadow-report.json"
    report = write_report(proposal, baseline, shadow, report_path)

    print("\n=== Shadow application complete ===")
    print(f"Recommendation: {report['recommendation']}")


if __name__ == "__main__":
    main()
