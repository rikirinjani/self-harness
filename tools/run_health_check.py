#!/usr/bin/env python3
"""Run Health Check — Phase 7

Quick operational health check for the Self-Harness Program.

Usage:
    python tools/run_health_check.py
    python tools/run_health_check.py --json
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


def run(cmd, cwd=ROOT, check=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if check and result.returncode != 0:
        print(f"Command failed: {' '.join(str(c) for c in cmd)}\n{result.stderr}", file=sys.stderr)
        return None
    return result.stdout


def benchmark_summary():
    out = run([sys.executable, str(ROOT / "benchmarks" / "run.py"), "--summary"])
    if out is None:
        return None, "benchmark summary failed"
    try:
        return json.loads(out), None
    except json.JSONDecodeError as e:
        return None, f"invalid benchmark JSON: {e}"


def trace_clean():
    out = run([sys.executable, str(ROOT / "tools" / "retrace.py")], check=False)
    if out is None:
        return False, "retrace scanner failed"
    ok = "trace-clean" in out or "All project files appear in at least one trace" in out
    return ok, None


def pending_promotions():
    return list((ROOT / "shadow" / "reports").glob("*-awaiting-approval.json"))


def git_uncommitted():
    out = run(["git", "status", "--short"], check=False)
    if out is None:
        return []
    return [line for line in out.splitlines() if line.strip()]


def phase_statuses():
    statuses = {}
    for path in (ROOT / "phases").glob("phase-*-progress.md"):
        text = path.read_text(encoding="utf-8")
        status_match = re.search(r"\*\*Status:\*\*\s*(.+)", text)
        statuses[path.stem] = status_match.group(1).strip() if status_match else "unknown"
    return statuses


def main():
    parser = argparse.ArgumentParser(description="Self-Harness health check")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    summary, summary_err = benchmark_summary()
    trace_ok, trace_err = trace_clean()
    pending = pending_promotions()
    uncommitted = git_uncommitted()
    phases = phase_statuses()

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "benchmark_summary": summary,
        "benchmark_summary_error": summary_err,
        "trace_clean": trace_ok,
        "trace_clean_error": trace_err,
        "pending_promotions": [p.stem for p in pending],
        "uncommitted_changes": uncommitted,
        "phase_statuses": phases,
        "overall_healthy": summary is not None and trace_ok,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Health check at {report['timestamp']}")
        print(f"  Benchmark summary: {'OK' if summary else 'FAIL'}" + (f" ({summary_err})" if summary_err else ""))
        if summary:
            print(f"    Pass rate: {summary.get('pass_rate', 0):.1f}%")
            print(f"    Passed: {summary.get('passed', 0)}/{summary.get('total_benchmarks', 0)}")
        print(f"  Trace clean: {'OK' if trace_ok else 'FAIL'}" + (f" ({trace_err})" if trace_err else ""))
        print(f"  Pending promotions: {len(pending)}")
        print(f"  Uncommitted changes: {len(uncommitted)}")
        print(f"  Phase statuses:")
        for name, status in sorted(phases.items()):
            print(f"    {name}: {status}")
        print(f"\nOverall: {'HEALTHY' if report['overall_healthy'] else 'UNHEALTHY'}")

    if not report["overall_healthy"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
