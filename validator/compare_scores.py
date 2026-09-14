#!/usr/bin/env python3
"""Compare Phase 2 executor scores with GPT validation scores.

Usage:
    # After filling in GPT responses, run:
    python validator/compare_scores.py                     # Compare all
    python validator/compare_scores.py BENCH-R             # Filter by prefix
    python validator/compare_scores.py --json              # JSON output

How to use:
    1. Open validator/prompts/BENCH-X-NN.txt in GPT
    2. Fill in scores (replace ___ with numbers 1-5)
    3. Fill in weaknesses and strengths
    4. Save response as validator/responses/BENCH-X-NN.txt
    5. Run this script to compare
"""

import argparse
import json
import re
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = THIS_DIR / "prompts"
RESPONSES_DIR = THIS_DIR / "responses"
COMPARISONS_DIR = THIS_DIR / "comparisons"

QUALITY_AXES = [
    "correctness", "completeness", "clarity", "reasoning",
    "precision", "efficiency", "actionability", "faithfulness",
]


def parse_response(text):
    """Extract scores and verdict from GPT response text."""
    scores = {}
    for ax in QUALITY_AXES:
        # Match patterns like "1. correctness (1-5): 4" or "1. correctness (1-5): 4   note: ..."
        patterns = [
            rf"{QUALITY_AXES.index(ax)+1}\.\s*{re.escape(ax)}\s*\(1-5\):\s*(\d)",
            rf"{re.escape(ax)}.*?\(1-5\):\s*(\d)",
        ]
        found = False
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                val = int(m.group(1))
                if 1 <= val <= 5:
                    scores[ax] = val
                    found = True
                    break
        if not found:
            scores[ax] = None

    # Extract verdict
    verdict = None
    m = re.search(r"OVERALL VERDICT:\s*(Pass|Fail)", text, re.IGNORECASE)
    if m:
        verdict = m.group(1).lower()

    # Extract weaknesses (simple heuristic)
    weaknesses = []
    in_weakness = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("WEAKNESSES") or stripped.startswith("Weaknesses"):
            in_weakness = True
            continue
        if in_weakness:
            if stripped.startswith("STRENGTHS") or stripped.startswith("Strengths"):
                break
            if stripped.startswith("OVERALL VERDICT"):
                break
            # Match numbered items or bullet points
            m = re.match(r"^\d+\.?\s*(.+?)(?:$|(?=\s+\d+\.))", stripped)
            if m:
                weaknesses.append(m.group(1).strip())
            elif stripped.startswith("- ") or stripped.startswith("* "):
                weaknesses.append(stripped[2:].strip())
            elif stripped and not stripped.startswith("___"):
                weaknesses.append(stripped)

    return {"scores": scores, "verdict": verdict, "weaknesses": weaknesses}


def load_executor_scores():
    """Load Phase 2 executor scores from result JSON files."""
    results_dir = THIS_DIR.parent / "benchmarks" / "results"
    scores = {}
    for rf in sorted(results_dir.glob("BENCH-*.json")):
        if rf.name == "summary.json":
            continue
        data = json.loads(rf.read_text(encoding="utf-8"))
        bid = data.get("benchmark_id", rf.stem)
        sc = data.get("scores", {})
        avg = sc.get("average")
        scores[bid] = {
            "scores": {ax: sc.get(ax) for ax in QUALITY_AXES},
            "average": avg,
            "outcome": data.get("execution", {}).get("outcome"),
            "weaknesses": data.get("weaknesses", []),
        }
    return scores


def generate_comparison_report(bench_ids, executor, gpt, output_file=None):
    """Generate comparison report between executor and GPT scores."""
    lines = [
        "# Score Comparison: Phase 2 Executor vs GPT Validator",
        f"",
        f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"| Benchmark | Axes Matched | Exec Avg | GPT Avg | Diff | Exec Verdict | GPT Verdict |",
        f"|-----------|-------------|----------|---------|------|--------------|-------------|",
    ]

    total_exec_avg = 0
    total_gpt_avg = 0
    count = 0
    total_diff = 0
    flagged = []

    for bid in bench_ids:
        e = executor.get(bid, {})
        g = gpt.get(bid, {})
        e_scores = e.get("scores", {})
        g_scores = g.get("scores", {})

        e_avg = round(sum(v for v in e_scores.values() if v) / len(QUALITY_AXES), 2) if any(e_scores.values()) else 0
        g_avg = round(sum(v for v in g_scores.values() if v) / len(QUALITY_AXES), 2) if any(g_scores.values()) else 0

        axes_matched = sum(1 for ax in QUALITY_AXES
                          if e_scores.get(ax) and g_scores.get(ax))
        diff = round(abs(e_avg - g_avg), 2)

        if g_scores and any(g_scores.values()):
            total_exec_avg += e_avg
            total_gpt_avg += g_avg
            total_diff += diff
            count += 1

        e_verdict = e.get("outcome", "?")
        g_verdict = g.get("verdict", "?")
        diff_marker = " ⚠️" if diff > 1.5 else ""

        lines.append(
            f"| {bid} | {axes_matched}/8 | {e_avg:.2f} | {g_avg:.2f} | {diff:.2f}{diff_marker} | {e_verdict} | {g_verdict} |"
        )

        if diff > 1.5:
            flagged.append((bid, e_avg, g_avg, diff, e_scores, g_scores))

    if count > 0:
        lines.extend([
            "",
            f"**Overall:** Executor avg {total_exec_avg/count:.2f} vs GPT avg {total_gpt_avg/count:.2f} "
            f"(avg diff {total_diff/count:.2f})",
            f"**Agreement rate (within ±1.0):** {sum(1 for b in bench_ids if abs((executor.get(b,{})).get('average',0) - (gpt.get(b,{})).get('scores',{}).get('average',0) if gpt.get(b,{}).get('scores',{}) else 0) <= 1) / count * 100:.0f}%"
            if count > 0 else "**No data**",
        ])

    if flagged:
        lines.extend(["", "## Flagged Benchmarks (diff > 1.5)", ""])
        for bid, e_avg, g_avg, diff, e_scores, g_scores in flagged:
            lines.append(f"### {bid} (diff={diff})")
            lines.append("")
            lines.append("| Axis | Executor | GPT |")
            lines.append("|------|----------|-----|")
            for ax in QUALITY_AXES:
                ev = e_scores.get(ax, "-")
                gv = g_scores.get(ax, "-")
                lines.append(f"| {ax} | {ev} | {gv} |")
            lines.append("")

    output = "\n".join(lines)

    if output_file:
        output_file.write_text(output, encoding="utf-8")
        print(f"Report saved to {output_file}")

    return output, flagged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filter", nargs="?", help="Filter by prefix (e.g. BENCH-R)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    COMPARISONS_DIR.mkdir(parents=True, exist_ok=True)

    executor = load_executor_scores()
    if not executor:
        print("Error: no executor scores found in benchmarks/results/")
        sys.exit(1)

    # Load GPT responses
    gpt_scores = {}
    for rf in sorted(RESPONSES_DIR.glob("BENCH-*.txt")):
        bid = rf.stem
        parsed = parse_response(rf.read_text(encoding="utf-8"))
        gpt_scores[bid] = parsed
        print(f"  [loaded] {bid}: avg={sum(v for v in parsed['scores'].values() if v)/len(QUALITY_AXES):.2f}" if any(parsed['scores'].values()) else f"  [loaded] {bid}: (no scores parsed)")

    if not gpt_scores:
        print("No GPT responses found in validator/responses/")
        print(f"Place GPT-filled files in: {RESPONSES_DIR}")
        print(f"Prompt files are in: {PROMPTS_DIR}")
        sys.exit(1)

    # Determine benchmarks to compare
    bench_ids = sorted(set(list(executor.keys()) + list(gpt_scores.keys())))
    if args.filter:
        bench_ids = [b for b in bench_ids if b.startswith(args.filter.upper())]

    report, flagged = generate_comparison_report(bench_ids, executor, gpt_scores,
                                                  COMPARISONS_DIR / "comparison_report.md")
    print("\n" + report)

    if args.json:
        data = {
            "executor": executor,
            "gpt": gpt_scores,
            "flagged": [{"benchmark": b[0], "exec_avg": b[1], "gpt_avg": b[2], "diff": b[3]} for b in flagged],
        }
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
