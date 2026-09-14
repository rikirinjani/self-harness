#!/usr/bin/env python3
"""Daily Weakness Check — Phase 4

Runs the weakness miner, compares results to the previous run, generates
proposals for new or worsening themes, and updates the operational dashboard.

Usage:
    python tools/daily_weakness_check.py
    python tools/daily_weakness_check.py --proposals 3
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PROPOSALS_DIR = ROOT / "proposals"
OPS_DIR = ROOT / "ops"
DASHBOARD_FILE = OPS_DIR / "dashboard.md"
HISTORY_FILE = OPS_DIR / "weakness_history.json"


def run_weakness_miner_json():
    """Run the weakness miner and return parsed JSON report."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_path = PROPOSALS_DIR / f"weakness-miner-report-{timestamp}.json"
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "weakness_miner.py"), "--json", "--output", str(report_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"Weakness miner failed:\n{result.stderr}")
        sys.exit(1)
    data = json.loads(report_path.read_text(encoding="utf-8"))
    return data, report_path


def load_history():
    """Load previous weakness check history."""
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    return []


def save_history(history):
    """Save weakness check history."""
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def theme_key(theme):
    """Stable key for a theme."""
    return theme.get("theme", "")


def find_new_or_worsening(current, previous):
    """Compare current themes to previous and return changed ones."""
    if not previous:
        return current.get("ranked_candidates", [])[:3]

    prev = previous[-1]
    prev_themes = {theme_key(t): t for t in prev.get("themes", [])}
    changes = []
    for t in current.get("themes", []):
        key = theme_key(t)
        if key not in prev_themes:
            changes.append(t)
            continue
        prev_score = prev_themes[key].get("score", 0)
        if t.get("score", 0) > prev_score * 1.2:
            changes.append(t)
    return changes


def generate_proposals_for_themes(themes, max_proposals):
    """Invoke proposal generator for each new/worsening theme."""
    generated = []
    for rank, theme in enumerate(themes[:max_proposals], 1):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "propose_harness_change.py"), "--rank", str(rank)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("  File: "):
                    generated.append(line.replace("  File: ", ""))
        else:
            print(f"Proposal generation failed for rank {rank}:\n{result.stderr}")
    return generated


def update_dashboard(current, previous, generated):
    """Update or create the operational dashboard."""
    OPS_DIR.mkdir(parents=True, exist_ok=True)
    summary = current.get("summary", {})
    prev_summary = previous[-1].get("summary", {}) if previous else {}

    def delta(key):
        cur = summary.get(key, 0)
        pre = prev_summary.get(key, 0)
        d = cur - pre
        return f"+{d}" if d > 0 else f"{d}"

    lines = [
        "# Self-Harness Operational Dashboard",
        "",
        f"**Last updated:** {datetime.now(timezone.utc).isoformat()}Z",
        "",
        "## Current Health",
        "",
        "| Metric | Current | Δ vs previous |",
        "|--------|--------:|---------------:|",
        f"| Flagged benchmarks | {summary.get('flagged', 0)} | {delta('flagged')} |",
        f"| Avg diff | {summary.get('avg_diff', 0):.2f} | {delta('avg_diff')} |",
        f"| Agreement rate | {summary.get('agreement', 0):.0%} | {delta('agreement')} |",
        f"| Failure records | {summary.get('failure_records', 0)} | {delta('failure_records')} |",
        f"| Trace records | {summary.get('trace_records', 0)} | {delta('trace_records')} |",
        "",
        "## Top Weakness Themes",
        "",
        "| Rank | Theme | Source | Priority | Score |",
        "|------|-------|--------|----------|------:|",
    ]
    for i, t in enumerate(current.get("ranked_candidates", [])[:5], 1):
        lines.append(f"| {i} | {t['theme']} | {t.get('source', '')} | {t.get('priority', 'low')} | {t.get('score', 0)} |")

    lines.extend([
        "",
        "## Recently Auto-Generated Proposals",
        "",
    ])
    if generated:
        for g in generated:
            lines.append(f"- `{Path(g).name}`")
    else:
        lines.append("- None this run.")

    lines.append("")
    DASHBOARD_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Dashboard updated: {DASHBOARD_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Daily weakness check")
    parser.add_argument("--proposals", type=int, default=3, help="Max proposals to generate for new/worsening themes")
    args = parser.parse_args()

    print("Running daily weakness check...")
    current, report_path = run_weakness_miner_json()
    print(f"Report: {report_path}")

    history = load_history()
    changes = find_new_or_worsening(current, history)

    generated = []
    if changes:
        print(f"Detected {len(changes)} new or worsening theme(s). Generating up to {args.proposals} proposals...")
        generated = generate_proposals_for_themes(changes, args.proposals)
    else:
        print("No new or worsening themes. Skipping proposal generation.")

    update_dashboard(current, history, generated)

    history.append(current)
    save_history(history)

    print("\n=== Daily check complete ===")
    print(f"Flagged: {current['summary']['flagged']}, avg diff: {current['summary']['avg_diff']:.2f}")
    print(f"Proposals generated: {len(generated)}")


if __name__ == "__main__":
    main()
