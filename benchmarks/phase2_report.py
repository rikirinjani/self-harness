#!/usr/bin/env python3
"""Phase 2 Completion Report Generator.

Usage:
    python benchmarks/phase2_report.py                         # Print report
    python benchmarks/phase2_report.py --output phase2.md      # Save to file
    python benchmarks/phase2_report.py --json                   # JSON output
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
RESULTS_DIR = THIS_DIR / "results"
OUTPUTS_DIR = THIS_DIR / "outputs"


def collect_results(results_dir):
    """Read all benchmark result files. Handles missing dir gracefully."""
    results_dir = Path(results_dir)
    if not results_dir.exists():
        return [], f"Error: results directory not found at {results_dir}"

    results = []
    errors = []
    for rf in sorted(results_dir.glob("BENCH-*.json")):
        if rf.name == "summary.json":
            continue
        try:
            with open(rf, encoding="utf-8") as f:
                data = json.load(f)
            results.append(data)
        except (json.JSONDecodeError, OSError) as e:
            errors.append(f"  {rf.name}: {e}")

    return results, errors


def check_gate(results, total_expected=20):
    """Check Phase 2 exit gate conditions."""
    gates = {
        "Runner script exists": Path(THIS_DIR / "run.py").exists(),
        "All 20 benchmarks executed": len(results) >= total_expected,
        ">=5 weaknesses identified": (
            sum(len(r.get("weaknesses", [])) for r in results) >= 5
        ),
        "Results recorded": len(results) > 0,
    }
    gates["All results have trace references"] = all(
        r.get("trace_ref") for r in results if r.get("trace_ref")
    )

    passed = sum(1 for v in gates.values() if v)
    total = len(gates)
    return gates, passed, total


def generate_report(results, errors=None):
    """Generate structured markdown report."""
    errors = errors or []
    total = len(results)
    passed = sum(1 for r in results if r.get("execution", {}).get("outcome") == "pass")
    failed = total - passed

    scores = [
        r.get("scores", {}).get("average", 0) or 0 for r in results
    ]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    weaknesses = []
    for r in results:
        weaknesses.extend(r.get("weaknesses", []))

    gates, gates_passed, gates_total = check_gate(results)

    lines = [
        f"# Phase 2 Completion Report",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Status:** {'COMPLETE' if gates_passed == gates_total else 'INCOMPLETE'}",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total benchmarks | {total} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| Average score | {avg_score} |",
        f"| Total weaknesses | {len(weaknesses)} |",
        f"",
    ]

    # Per-benchmark detail
    lines.extend([
        f"## Benchmark Details",
        f"",
        f"| ID | Score | Outcome | Duration | Weaknesses |",
        f"|----|-------|---------|----------|------------|",
    ])
    for r in results:
        bid = r.get("benchmark_id", "?")
        sc = r.get("scores", {}).get("average", "?")
        oc = r.get("execution", {}).get("outcome", "?")
        du = r.get("execution", {}).get("duration_s", "?")
        wc = len(r.get("weaknesses", []))
        lines.append(f"| {bid} | {sc} | {oc} | {du}s | {wc} |")

    # Gate status
    lines.extend([
        f"",
        f"## Phase-Out Gate Status",
        f"",
        f"| Gate | Status |",
        f"|------|--------|",
    ])
    for gate, status in gates.items():
        icon = "[x]" if status else "[ ]"
        lines.append(f"| {gate} | {icon} |")

    # Weaknesses
    if weaknesses:
        lines.extend([
            f"",
            f"## Weaknesses ({len(weaknesses)})",
            f"",
        ])
        for i, w in enumerate(weaknesses[:30], 1):
            lines.append(f"{i}. {w}")
        if len(weaknesses) > 30:
            lines.append(f"... +{len(weaknesses) - 30} more")

    # Errors
    if errors:
        lines.extend([
            f"",
            f"## File Errors",
            f"",
        ])
        for e in errors:
            lines.append(f"- {e}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Phase 2 Completion Report Generator")
    parser.add_argument("--output", help="Save report to file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results, errors = collect_results(RESULTS_DIR)

    if not results and not errors:
        print("Error: no results found and no errors to report")
        sys.exit(1)

    if args.json:
        output = json.dumps({
            "generated": datetime.now().isoformat(),
            "total": len(results),
            "passed": sum(1 for r in results if r.get("execution", {}).get("outcome") == "pass"),
            "avg_score": round(
                sum(r.get("scores", {}).get("average", 0) or 0 for r in results) / len(results), 2
            ) if results else 0,
            "weakness_count": sum(len(r.get("weaknesses", [])) for r in results),
            "errors": len(errors),
        }, indent=2)
    else:
        output = generate_report(results, errors)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output, encoding="utf-8")
        print(f"Report saved to {out_path.resolve()}")
    else:
        print(output)


if __name__ == "__main__":
    main()
