#!/usr/bin/env python3
"""Weakness Miner — Phase 3

Reads the benchmark summary, validator comparison report, and failure records,
then clusters weaknesses into themes and ranks harness improvement candidates.

Usage:
    python tools/weakness_miner.py
    python tools/weakness_miner.py --output proposals/weakness-miner-report-YYYY-MM-DD.md
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
BENCHMARKS_RESULTS = ROOT / "benchmarks" / "results" / "summary.json"
COMPARISON_REPORT = ROOT / "validator" / "comparisons" / "comparison_report.md"
FAILURES_DIR = ROOT / "failures"
PROPOSALS_DIR = ROOT / "proposals"

QUALITY_AXES = [
    "correctness", "completeness", "clarity", "reasoning",
    "precision", "efficiency", "actionability", "faithfulness",
]


def parse_comparison_report(path):
    """Parse the markdown comparison table into structured rows."""
    text = path.read_text(encoding="utf-8")
    rows = []
    # Match table rows like: | BENCH-C-01 | 8/8 | 5.00 | 3.12 | 1.88 ⚠️ | pass | fail |
    pattern = re.compile(
        r"\|\s*(BENCH-[A-Z]-\d+)\s*\|\s*(\d+/\d+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*"
    )
    for m in pattern.finditer(text):
        bid, axes, exec_avg, gpt_avg, diff = m.groups()
        rows.append({
            "benchmark": bid,
            "axes_matched": axes,
            "exec_avg": float(exec_avg),
            "gpt_avg": float(gpt_avg),
            "diff": float(diff),
        })
    # Extract per-axis diffs for flagged sections
    flagged = {}
    current = None
    for line in text.splitlines():
        header = re.match(r"### (BENCH-[A-Z]-\d+) \(diff=[\d.]+\)", line)
        if header:
            current = header.group(1)
            flagged[current] = {}
            continue
        if current:
            m = re.match(r"\|\s*(\w+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", line)
            if m and m.group(1) in QUALITY_AXES:
                axis, exec_s, gpt_s = m.groups()
                flagged[current][axis] = {
                    "exec": int(exec_s),
                    "gpt": int(gpt_s),
                    "diff": int(exec_s) - int(gpt_s),
                }
    return rows, flagged


def parse_failures():
    """Load all failure records and bucket by category."""
    failures = []
    for fp in sorted(FAILURES_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        failures.append({
            "file": fp.name,
            "category": data.get("category", "unknown"),
            "severity": data.get("severity", "unknown"),
            "root_cause": data.get("root_cause", ""),
            "agent": data.get("failure_signature", {}).get("agent", "unknown"),
        })
    return failures


def cluster_weaknesses(rows, flagged, failures):
    """Generate ranked weakness themes."""
    themes = []

    # Theme 1: category-level inflation
    coding = [r for r in rows if r["benchmark"].startswith("BENCH-C")]
    if coding:
        avg_diff = sum(r["diff"] for r in coding) / len(coding)
        if avg_diff > 1.0:
            themes.append({
                "theme": "Executor score inflation on coding benchmarks",
                "diff": round(avg_diff, 2),
                "benchmarks": [r["benchmark"] for r in coding],
                "affected_axes": ["correctness", "actionability", "faithfulness"],
                "evidence": "GPT validator frequently marks coding outputs fail while executor marks pass.",
                "priority": "high",
            })

    # Theme 2: low absolute validator scores
    low = [r for r in rows if r["gpt_avg"] < 2.0]
    if low:
        themes.append({
            "theme": "Benchmarks producing outputs the validator rejects outright",
            "count": len(low),
            "benchmarks": [r["benchmark"] for r in low],
            "evidence": "GPT validator avg < 2.0 suggests outputs miss core requirements.",
            "priority": "high",
        })

    # Theme 3: faithfulness deficits in coding
    faithfulness_gaps = []
    for bid, axes in flagged.items():
        if axes.get("faithfulness", {}).get("diff", 0) > 2:
            faithfulness_gaps.append(bid)
    if faithfulness_gaps:
        themes.append({
            "theme": "Low faithfulness scores on coding/operational outputs",
            "benchmarks": faithfulness_gaps,
            "evidence": "Large exec-gpt gap on faithfulness axis indicates outputs may not follow constraints precisely.",
            "priority": "high",
        })

    # Theme 4: actionability gaps
    actionability_gaps = []
    for bid, axes in flagged.items():
        if axes.get("actionability", {}).get("diff", 0) > 2:
            actionability_gaps.append(bid)
    if actionability_gaps:
        themes.append({
            "theme": "Outputs score high on actionability internally but low externally",
            "benchmarks": actionability_gaps,
            "evidence": "Validator finds outputs not directly usable despite executor passing them.",
            "priority": "medium",
        })

    # Theme 5: failure taxonomy concentration
    if failures:
        cat_counts = Counter(f["category"] for f in failures)
        top = cat_counts.most_common(3)
        themes.append({
            "theme": "Recurring failure categories in backlog",
            "categories": top,
            "evidence": f"Top failure categories across {len(failures)} records.",
            "priority": "medium",
        })

    return themes


def rank_candidates(themes, rows):
    """Rank harness improvement candidates."""
    candidates = []
    for t in themes:
        score = 0
        if t.get("priority") == "high":
            score += 3
        elif t.get("priority") == "medium":
            score += 2
        else:
            score += 1
        score += len(t.get("benchmarks", []))
        if "diff" in t:
            score += t["diff"]
        candidates.append({"theme": t["theme"], "score": score, **t})
    return sorted(candidates, key=lambda x: x["score"], reverse=True)


def generate_report(output_path=None):
    rows, flagged = parse_comparison_report(COMPARISON_REPORT)
    failures = parse_failures()
    themes = cluster_weaknesses(rows, flagged, failures)
    candidates = rank_candidates(themes, rows)

    flagged_count = sum(1 for r in rows if r["diff"] > 1.5)
    avg_diff = sum(r["diff"] for r in rows) / len(rows) if rows else 0.0
    agreement = sum(1 for r in rows if r["diff"] <= 1.0) / len(rows) if rows else 0.0

    lines = [
        "# Weakness Miner Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}Z",
        f"**Source:** {COMPARISON_REPORT.name}",
        "",
        "## Summary",
        "",
        f"- Total benchmarks: {len(rows)}",
        f"- Flagged benchmarks (diff > 1.5): {flagged_count}",
        f"- Average executor/validator diff: {avg_diff:.2f}",
        f"- Agreement rate (diff ≤ 1.0): {agreement:.0%}",
        f"- Failure records analyzed: {len(failures)}",
        "",
        "## Flagged Benchmarks",
        "",
        "| Benchmark | Exec Avg | GPT Avg | Diff |",
        "|-----------|----------|---------|------|",
    ]
    for r in rows:
        if r["diff"] > 1.5:
            lines.append(f"| {r['benchmark']} | {r['exec_avg']:.2f} | {r['gpt_avg']:.2f} | {r['diff']:.2f} |")
    lines.append("")
    lines.append("## Weakness Themes")
    lines.append("")
    for i, t in enumerate(themes, 1):
        lines.append(f"### {i}. {t['theme']} (priority: {t.get('priority', 'low')})")
        lines.append("")
        lines.append(f"- **Evidence:** {t.get('evidence', '')}")
        if "benchmarks" in t:
            lines.append(f"- **Benchmarks:** {', '.join(t['benchmarks'])}")
        if "categories" in t:
            lines.append(f"- **Top categories:** {', '.join(f'{cat} ({n})' for cat, n in t['categories'])}")
        if "affected_axes" in t:
            lines.append(f"- **Axes most affected:** {', '.join(t['affected_axes'])}")
        lines.append("")

    lines.append("## Ranked Improvement Candidates")
    lines.append("")
    lines.append("| Rank | Candidate | Score | Priority |")
    lines.append("|------|-----------|-------|----------|")
    for i, c in enumerate(candidates, 1):
        lines.append(f"| {i} | {c['theme']} | {c['score']} | {c.get('priority', 'low')} |")
    lines.append("")

    lines.append("## Proposed Next Steps")
    lines.append("")
    if candidates:
        top = candidates[0]
        lines.append(f"1. File a formal harness improvement proposal for: **{top['theme']}**")
        lines.append(f"2. Verify using benchmarks: {', '.join(top.get('benchmarks', [])[:3])}")
        lines.append("3. Implement the change in a feature branch.")
        lines.append("4. Run `tools/revalidate_benchmarks.py` and check that diff drops.")
    else:
        lines.append("No significant weakness themes detected. Re-run after collecting more validator data.")
    lines.append("")

    report_text = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(report_text, encoding="utf-8")
        print(f"Report saved to {output_path}")
    else:
        default_name = f"weakness-miner-report-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
        default_path = PROPOSALS_DIR / default_name
        default_path.write_text(report_text, encoding="utf-8")
        print(f"Report saved to {default_path}")

    print(f"\nSummary: {flagged_count} flagged, avg diff {avg_diff:.2f}, agreement {agreement:.0%}")
    return report_text


def main():
    parser = argparse.ArgumentParser(description="Self-Harness Weakness Miner")
    parser.add_argument("--output", help="Explicit output path for the report")
    args = parser.parse_args()
    generate_report(args.output)


if __name__ == "__main__":
    main()
