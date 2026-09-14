#!/usr/bin/env python3
"""Drift Monitor — Phase 7

Compares current program state to the previous recorded snapshot and writes
alerts when configurable thresholds are crossed.

Usage:
    python ops/drift_monitor.py
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OPS = ROOT / "ops"
ALERTS_DIR = OPS / "alerts"
WEAKNESS_HISTORY = OPS / "weakness_history.json"
THRESHOLDS = OPS / "thresholds.json"
LAST_STATE = OPS / "last_state.json"
DASHBOARD = OPS / "dashboard.md"
TRACES_DIR = ROOT / "traces"
FAILURES_DIR = ROOT / "failures"


def load_json(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def count_records(directory):
    if not directory.exists():
        return 0
    return sum(1 for p in directory.iterdir() if p.is_file())


def run_benchmark_summary():
    result = subprocess.run(
        [sys.executable, str(ROOT / "benchmarks" / "run.py"), "--summary"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        return None, result.stderr
    return json.loads(result.stdout), None


def check_thresholds(current, thresholds):
    """Return list of alert dicts."""
    alerts = []
    last = load_json(LAST_STATE) or {}

    avg_diff = current.get("avg_diff", 0.0)
    if avg_diff >= thresholds["avg_diff"]["critical"]:
        alerts.append({"level": "critical", "metric": "avg_diff", "value": avg_diff, "threshold": thresholds["avg_diff"]["critical"]})
    elif avg_diff >= thresholds["avg_diff"]["warning"]:
        alerts.append({"level": "warning", "metric": "avg_diff", "value": avg_diff, "threshold": thresholds["avg_diff"]["warning"]})

    failures = current.get("failure_records", 0)
    last_failures = last.get("failure_records", failures)
    delta_failures = failures - last_failures
    if delta_failures >= thresholds["failure_records_delta"]["critical"]:
        alerts.append({"level": "critical", "metric": "failure_records_delta", "value": delta_failures, "threshold": thresholds["failure_records_delta"]["critical"]})
    elif delta_failures >= thresholds["failure_records_delta"]["warning"]:
        alerts.append({"level": "warning", "metric": "failure_records_delta", "value": delta_failures, "threshold": thresholds["failure_records_delta"]["warning"]})

    traces = current.get("trace_records", 0)
    last_traces = last.get("trace_records", traces)
    delta_traces = traces - last_traces
    if delta_traces >= thresholds["trace_records_delta"]["critical"]:
        alerts.append({"level": "critical", "metric": "trace_records_delta", "value": delta_traces, "threshold": thresholds["trace_records_delta"]["critical"]})
    elif delta_traces >= thresholds["trace_records_delta"]["warning"]:
        alerts.append({"level": "warning", "metric": "trace_records_delta", "value": delta_traces, "threshold": thresholds["trace_records_delta"]["warning"]})

    pass_rate = current.get("pass_rate", 1.0)
    if pass_rate <= thresholds["pass_rate"]["critical"]:
        alerts.append({"level": "critical", "metric": "pass_rate", "value": pass_rate, "threshold": thresholds["pass_rate"]["critical"]})
    elif pass_rate <= thresholds["pass_rate"]["warning"]:
        alerts.append({"level": "warning", "metric": "pass_rate", "value": pass_rate, "threshold": thresholds["pass_rate"]["warning"]})

    pending = current.get("pending_promotions", 0)
    if pending >= thresholds["pending_promotions"]["critical"]:
        alerts.append({"level": "critical", "metric": "pending_promotions", "value": pending, "threshold": thresholds["pending_promotions"]["critical"]})
    elif pending >= thresholds["pending_promotions"]["warning"]:
        alerts.append({"level": "warning", "metric": "pending_promotions", "value": pending, "threshold": thresholds["pending_promotions"]["warning"]})

    return alerts


def write_alerts(alerts):
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    for level in ("warning", "critical"):
        level_alerts = [a for a in alerts if a["level"] == level]
        if level_alerts:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            path = ALERTS_DIR / f"{level}-{ts}.json"
            path.write_text(json.dumps(level_alerts, indent=2), encoding="utf-8")
            print(f"Wrote {path}")


def update_dashboard(current, alerts, themes):
    lines = [
        "# Self-Harness Operational Dashboard",
        "",
        f"**Last updated:** {datetime.now(timezone.utc).isoformat()}Z",
        "",
        "## Current Health",
        "",
        "| Metric | Current | Δ vs previous |",
        "|--------|--------:|---------------:|",
        f"| Flagged benchmarks | {current.get('flagged_benchmarks', 0)} | — |",
        f"| Avg diff | {current.get('avg_diff', 0.0):.2f} | — |",
        f"| Pass rate | {current.get('pass_rate', 1.0):.2%} | — |",
        f"| Failure records | {current.get('failure_records', 0)} | +{current.get('failure_records', 0) - (load_json(LAST_STATE) or {}).get('failure_records', current.get('failure_records', 0))} |",
        f"| Trace records | {current.get('trace_records', 0)} | +{current.get('trace_records', 0) - (load_json(LAST_STATE) or {}).get('trace_records', current.get('trace_records', 0))} |",
        f"| Pending promotions | {current.get('pending_promotions', 0)} | — |",
        "",
        "## Alerts",
        "",
    ]
    if alerts:
        lines.append("| Level | Metric | Value | Threshold |")
        lines.append("|-------|--------|------:|----------:|")
        for a in alerts:
            lines.append(f"| {a['level']} | {a['metric']} | {a['value']} | {a['threshold']} |")
    else:
        lines.append("No threshold alerts at this time.")
    lines.extend([
        "",
        "## Top Weakness Themes",
        "",
        "| Rank | Theme | Source | Priority |",
        "|------|-------|--------|----------|",
    ])
    for i, t in enumerate(themes[:5], 1):
        lines.append(f"| {i} | {t['theme']} | {t.get('source', '-')} | {t.get('priority', '-')} |")
    lines.append("")
    DASHBOARD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated {DASHBOARD}")


def main():
    thresholds = load_json(THRESHOLDS)
    if not thresholds:
        print(f"Thresholds not found: {THRESHOLDS}")
        sys.exit(1)

    summary, err = run_benchmark_summary()
    if err:
        print(f"Benchmark summary failed: {err}")
        sys.exit(1)

    history = load_json(WEAKNESS_HISTORY) or []
    latest = history[-1] if history else {}
    flagged = len(latest.get("flagged_benchmarks", []))
    avg_diff = latest.get("summary", {}).get("avg_diff", 0.0)
    failure_records = count_records(FAILURES_DIR)
    trace_records = count_records(TRACES_DIR)
    pending_promotions = len(list((ROOT / "shadow" / "reports").glob("*-awaiting-approval.json")))
    pass_rate = summary.get("pass_rate", 1.0) / 100.0 if summary.get("pass_rate", 0) > 1 else summary.get("pass_rate", 1.0)

    current = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "flagged_benchmarks": flagged,
        "avg_diff": avg_diff,
        "pass_rate": pass_rate,
        "failure_records": failure_records,
        "trace_records": trace_records,
        "pending_promotions": pending_promotions,
    }

    alerts = check_thresholds(current, thresholds)
    write_alerts(alerts)
    update_dashboard(current, alerts, latest.get("themes", []))

    # Save state for next comparison
    LAST_STATE.write_text(json.dumps(current, indent=2), encoding="utf-8")

    if alerts:
        levels = ", ".join(sorted(set(a["level"] for a in alerts)))
        print(f"Drift detected: {levels}")
        sys.exit(0 if all(a["level"] == "warning" for a in alerts) else 2)
    print("No drift detected.")


if __name__ == "__main__":
    main()
