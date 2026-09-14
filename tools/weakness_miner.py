#!/usr/bin/env python3
"""Weakness Miner — Phase 4

Reads benchmark summary, validator comparison report, failure records, and trace
records, then clusters weaknesses into themes, correlates across sources, and
ranks harness improvement candidates.

Usage:
    python tools/weakness_miner.py
    python tools/weakness_miner.py --output proposals/weakness-miner-report-YYYY-MM-DD.md
    python tools/weakness_miner.py --json --output proposals/weakness-miner-report.json
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
TRACES_DIR = ROOT / "traces"
PROPOSALS_DIR = ROOT / "proposals"

QUALITY_AXES = [
    "correctness", "completeness", "clarity", "reasoning",
    "precision", "efficiency", "actionability", "faithfulness",
]

TRACE_AGENT_RE = re.compile(r'"agent"\s*:\s*"([^"]+)"')
TRACE_RECORD_RE = re.compile(r'"record_type"\s*:\s*"([^"]+)"')
TRACE_ACTION_RE = re.compile(r'"action"\s*:\s*"([^"]+)"')


def parse_comparison_report(path):
    """Parse the markdown comparison table into structured rows."""
    text = path.read_text(encoding="utf-8")
    rows = []
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
    """Load all failure records and bucket by category, agent, severity."""
    failures = []
    for fp in sorted(FAILURES_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        sig = data.get("failure_signature", {}) or {}
        failures.append({
            "file": fp.name,
            "category": data.get("category", "unknown"),
            "severity": data.get("severity", "unknown"),
            "root_cause": data.get("root_cause", ""),
            "agent": sig.get("agent", "unknown"),
            "cause": sig.get("cause", "unknown"),
            "timestamp": data.get("timestamp", ""),
        })
    return failures


def parse_traces():
    """Load trace metadata from .pm1 and .json trace files."""
    traces = []
    for fp in list(TRACES_DIR.glob("*.pm1")) + list(TRACES_DIR.glob("*.json")):
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        agent = "unknown"
        record_type = "unknown"
        action = ""
        m = TRACE_AGENT_RE.search(text)
        if m:
            agent = m.group(1)
        m = TRACE_RECORD_RE.search(text)
        if m:
            record_type = m.group(1)
        m = TRACE_ACTION_RE.search(text)
        if m:
            action = m.group(1)
        traces.append({
            "file": fp.name,
            "agent": agent,
            "record_type": record_type,
            "action": action,
        })
    return traces


def cluster_benchmark_weaknesses(rows, flagged):
    """Generate themes from benchmark comparison data."""
    themes = []

    coding = [r for r in rows if r["benchmark"].startswith("BENCH-C")]
    if coding:
        avg_diff = sum(r["diff"] for r in coding) / len(coding)
        if avg_diff > 1.0:
            themes.append({
                "theme": "Executor score inflation on coding benchmarks",
                "source": "benchmark",
                "diff": round(avg_diff, 2),
                "benchmarks": [r["benchmark"] for r in coding],
                "affected_axes": ["correctness", "actionability", "faithfulness"],
                "evidence": "GPT validator frequently marks coding outputs fail while executor marks pass.",
                "priority": "high",
            })

    low = [r for r in rows if r["gpt_avg"] < 2.0]
    if low:
        themes.append({
            "theme": "Benchmarks producing outputs the validator rejects outright",
            "source": "benchmark",
            "count": len(low),
            "benchmarks": [r["benchmark"] for r in low],
            "evidence": "GPT validator avg < 2.0 suggests outputs miss core requirements.",
            "priority": "high",
        })

    for axis in QUALITY_AXES:
        gaps = []
        for bid, axes in flagged.items():
            if axes.get(axis, {}).get("diff", 0) > 2:
                gaps.append(bid)
        if gaps:
            themes.append({
                "theme": f"Low {axis} scores on flagged benchmarks",
                "source": "benchmark",
                "benchmarks": gaps,
                "evidence": f"Large exec-gpt gap on {axis} axis.",
                "priority": "high" if axis in ("correctness", "faithfulness") else "medium",
                "affected_axes": [axis],
            })

    return themes


def cluster_failure_weaknesses(failures):
    """Generate themes from failure records."""
    themes = []
    if not failures:
        return themes

    cat_counts = Counter(f["category"] for f in failures)
    top = cat_counts.most_common(5)
    themes.append({
        "theme": "Recurring failure categories in backlog",
        "source": "failure",
        "categories": top,
        "evidence": f"Top failure categories across {len(failures)} records.",
        "priority": "high" if top and top[0][1] > 5 else "medium",
    })

    agent_counts = Counter(f["agent"] for f in failures if f["agent"] != "unknown")
    top_agents = agent_counts.most_common(5)
    if top_agents:
        themes.append({
            "theme": "Agents with highest failure counts",
            "source": "failure",
            "agents": top_agents,
            "evidence": "Agents that appear most frequently in failure records.",
            "priority": "medium",
        })

    cause_counts = Counter(f["cause"] for f in failures if f["cause"] != "unknown")
    top_causes = cause_counts.most_common(5)
    if top_causes:
        themes.append({
            "theme": "Recurring root-cause signatures",
            "source": "failure",
            "causes": top_causes,
            "evidence": "Repeated causal mechanisms across failures.",
            "priority": "high" if top_causes and top_causes[0][1] > 3 else "medium",
        })

    return themes


def cluster_trace_weaknesses(traces):
    """Generate themes from trace metadata."""
    themes = []
    if not traces:
        return themes

    agent_counts = Counter(t["agent"] for t in traces if t["agent"] != "unknown")
    top_agents = agent_counts.most_common(5)
    themes.append({
        "theme": "Most active agents in trace corpus",
        "source": "trace",
        "agents": top_agents,
        "evidence": f"Trace activity distribution across {len(traces)} records.",
        "priority": "low",
    })

    record_counts = Counter(t["record_type"] for t in traces if t["record_type"] != "unknown")
    top_records = record_counts.most_common(5)
    if top_records:
        themes.append({
            "theme": "Dominant trace record types",
            "source": "trace",
            "record_types": top_records,
            "evidence": "Which kinds of records dominate the trace database.",
            "priority": "low",
        })

    return themes


def correlate_themes(themes):
    """Find cross-source correlations."""
    by_name = defaultdict(list)
    for t in themes:
        by_name[t["theme"]].append(t)

    correlations = []
    benchmark_agents = {}
    failure_agents = {}

    for t in themes:
        if t["source"] == "benchmark" and "benchmarks" in t:
            for bid in t["benchmarks"]:
                benchmark_agents.setdefault(bid, []).append(t)
        if t["source"] == "failure" and "agents" in t:
            for agent, _ in t["agents"]:
                failure_agents.setdefault(agent, []).append(t)

    # Correlate benchmark themes with failure categories
    for t in themes:
        if t["source"] == "benchmark" and "affected_axes" in t:
            axis = t["affected_axes"][0]
            related = [f for f in themes if f["source"] == "failure" and axis in f.get("evidence", "")]
            if related:
                correlations.append({
                    "theme": f"Benchmark weakness '{t['theme']}' correlates with failure theme '{related[0]['theme']}'",
                    "sources": ["benchmark", "failure"],
                    "evidence": f"Both involve {axis} issues.",
                    "priority": "high",
                })

    return correlations


def rank_candidates(themes):
    """Rank harness improvement candidates."""
    candidates = []
    for t in themes:
        score = 0
        priority = t.get("priority", "low")
        if priority == "high":
            score += 3
        elif priority == "medium":
            score += 2
        else:
            score += 1
        score += len(t.get("benchmarks", []))
        score += len(t.get("categories", []))
        score += len(t.get("agents", []))
        if "diff" in t:
            score += t["diff"]
        candidates.append({"theme": t["theme"], "score": score, **t})
    return sorted(candidates, key=lambda x: x["score"], reverse=True)


def generate_report(output_path=None, as_json=False):
    rows, flagged = parse_comparison_report(COMPARISON_REPORT)
    failures = parse_failures()
    traces = parse_traces()

    benchmark_themes = cluster_benchmark_weaknesses(rows, flagged)
    failure_themes = cluster_failure_weaknesses(failures)
    trace_themes = cluster_trace_weaknesses(traces)
    correlations = correlate_themes(benchmark_themes + failure_themes + trace_themes)
    all_themes = benchmark_themes + failure_themes + trace_themes + correlations
    candidates = rank_candidates(all_themes)

    flagged_count = sum(1 for r in rows if r["diff"] > 1.5)
    avg_diff = sum(r["diff"] for r in rows) / len(rows) if rows else 0.0
    agreement = sum(1 for r in rows if r["diff"] <= 1.0) / len(rows) if rows else 0.0

    data = {
        "generated": datetime.now(timezone.utc).isoformat() + "Z",
        "summary": {
            "benchmarks": len(rows),
            "flagged": flagged_count,
            "avg_diff": round(avg_diff, 2),
            "agreement": round(agreement, 2),
            "failure_records": len(failures),
            "trace_records": len(traces),
            "evidence_sources": ["benchmark", "failure", "trace"],
        },
        "flagged_benchmarks": [
            {"benchmark": r["benchmark"], "exec_avg": r["exec_avg"], "gpt_avg": r["gpt_avg"], "diff": r["diff"]}
            for r in rows if r["diff"] > 1.5
        ],
        "themes": all_themes,
        "ranked_candidates": candidates,
    }

    if as_json:
        report_text = json.dumps(data, indent=2)
    else:
        lines = [
            "# Weakness Miner Report",
            "",
            f"**Generated:** {data['generated']}",
            f"**Sources:** benchmark comparison, failure records, trace metadata",
            "",
            "## Summary",
            "",
            f"- Total benchmarks: {data['summary']['benchmarks']}",
            f"- Flagged benchmarks (diff > 1.5): {data['summary']['flagged']}",
            f"- Average executor/validator diff: {data['summary']['avg_diff']:.2f}",
            f"- Agreement rate (diff ≤ 1.0): {data['summary']['agreement']:.0%}",
            f"- Failure records analyzed: {data['summary']['failure_records']}",
            f"- Trace records analyzed: {data['summary']['trace_records']}",
            f"- Evidence sources: {', '.join(data['summary']['evidence_sources'])}",
            "",
            "## Flagged Benchmarks",
            "",
            "| Benchmark | Exec Avg | GPT Avg | Diff |",
            "|-----------|----------|---------|------|",
        ]
        for r in data["flagged_benchmarks"]:
            lines.append(f"| {r['benchmark']} | {r['exec_avg']:.2f} | {r['gpt_avg']:.2f} | {r['diff']:.2f} |")
        lines.append("")
        lines.append("## Weakness Themes")
        lines.append("")
        for i, t in enumerate(all_themes, 1):
            lines.append(f"### {i}. {t['theme']} (source: {t['source']}, priority: {t.get('priority', 'low')})")
            lines.append("")
            lines.append(f"- **Evidence:** {t.get('evidence', '')}")
            if "benchmarks" in t:
                lines.append(f"- **Benchmarks:** {', '.join(t['benchmarks'])}")
            if "categories" in t:
                lines.append(f"- **Top categories:** {', '.join(f'{cat} ({n})' for cat, n in t['categories'])}")
            if "agents" in t:
                lines.append(f"- **Agents:** {', '.join(f'{agent} ({n})' for agent, n in t['agents'])}")
            if "affected_axes" in t:
                lines.append(f"- **Axes most affected:** {', '.join(t['affected_axes'])}")
            if "sources" in t:
                lines.append(f"- **Correlated sources:** {', '.join(t['sources'])}")
            lines.append("")

        lines.append("## Ranked Improvement Candidates")
        lines.append("")
        lines.append("| Rank | Candidate | Score | Priority | Source |")
        lines.append("|------|-----------|-------|----------|--------|")
        for i, c in enumerate(candidates, 1):
            lines.append(f"| {i} | {c['theme']} | {c['score']} | {c.get('priority', 'low')} | {c.get('source', '')} |")
        lines.append("")

        lines.append("## Proposed Next Steps")
        lines.append("")
        if candidates:
            top = candidates[0]
            lines.append(f"1. Generate a formal harness improvement proposal for: **{top['theme']}**")
            lines.append(f"2. Verify using benchmarks: {', '.join(top.get('benchmarks', [])[:3]) or 'TBD'}")
            lines.append("3. Implement the change in a feature branch.")
            lines.append("4. Run `tools/revalidate_benchmarks.py` and check that diff drops.")
        else:
            lines.append("No significant weakness themes detected. Re-run after collecting more evidence.")
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

    print(f"\nSummary: {data['summary']['flagged']} flagged, avg diff {data['summary']['avg_diff']:.2f}, "
          f"agreement {data['summary']['agreement']:.0%}, {data['summary']['failure_records']} failures, "
          f"{data['summary']['trace_records']} traces")
    return data, report_text


def main():
    parser = argparse.ArgumentParser(description="Self-Harness Weakness Miner")
    parser.add_argument("--output", help="Explicit output path for the report")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of Markdown")
    args = parser.parse_args()
    generate_report(args.output, args.json)


if __name__ == "__main__":
    main()
