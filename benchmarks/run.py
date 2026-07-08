#!/usr/bin/env python3
"""Self-harness Benchmark Runner -- Phase 2

Usage:
    python benchmarks/run.py --all                 # List all benchmarks
    python benchmarks/run.py BENCH-R-01            # Run a specific benchmark
    python benchmarks/run.py --category coding     # Run a category
    python benchmarks/run.py --score BENCH-R-01    # Score a completed benchmark
    python benchmarks/run.py --summary             # Show summary
    python benchmarks/run.py --dry-run BENCH-R-01  # Preview task without executing
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Reconfigure stdout to UTF-8 to handle Unicode characters on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


BENCHMARKS_DIR = Path(__file__).parent.resolve()
CATALOG_FILE = BENCHMARKS_DIR.parent / "benchmark_catalog.md"
RESULTS_DIR = BENCHMARKS_DIR / "results"
OUTPUTS_DIR = BENCHMARKS_DIR / "outputs"
SUMMARY_FILE = RESULTS_DIR / "summary.json"

QUALITY_AXES = ["correctness", "completeness", "clarity", "reasoning",
                "precision", "efficiency", "actionability", "faithfulness"]


class Benchmark:
    def __init__(self, benchmark_id, title, description, success_criteria,
                 failure_criteria, difficulty, responsible, category):
        self.id = benchmark_id
        self.title = title
        self.description = description
        self.success_criteria = success_criteria
        self.failure_criteria = failure_criteria
        self.difficulty = difficulty
        self.responsible = responsible
        self.category = category

    def __repr__(self):
        return f"{self.id}: {self.title} [{self.difficulty}]"


def parse_catalog(filepath):
    """Parse the markdown catalog into Benchmark objects."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    benchmarks = []
    # Split by category headings: ## Xxx Benchmarks
    sections = re.split(r"^## (\w+) Benchmarks", text, flags=re.MULTILINE)
    # sections[0] is everything before first heading (preamble)
    # then alternating: [category_name, content, category_name, content, ...]
    for i in range(1, len(sections), 2):
        category = sections[i].lower()
        content = sections[i + 1]

        # Parse benchmark blocks within content
        lines = content.strip().split("\n")
        j = 0
        while j < len(lines):
            line = lines[j].strip()
            m = re.match(r"### (BENCH-[\w-]+):\s*(.+)", line)
            if m:
                bench_id = m.group(1)
                title = m.group(2)
                fields = {}
                j += 1
                while j < len(lines) and not lines[j].strip().startswith("### BENCH-"):
                    stripped = lines[j].strip()
                    for prefix in ["Description", "Success criteria",
                                   "Failure criteria", "Difficulty", "Responsible"]:
                        if stripped.startswith(f"- **{prefix}:**"):
                            key = prefix.lower().replace(" ", "_")
                            parts = stripped.split(f":** ", 1)
                            fields[key] = parts[1] if len(parts) > 1 else ""
                            break
                    j += 1
                if all(k in fields for k in ["description", "success_criteria",
                                              "failure_criteria", "difficulty", "responsible"]):
                    benchmarks.append(Benchmark(
                        benchmark_id=bench_id, title=title,
                        description=fields["description"],
                        success_criteria=fields["success_criteria"],
                        failure_criteria=fields["failure_criteria"],
                        difficulty=fields["difficulty"],
                        responsible=fields["responsible"],
                        category=category
                    ))
                continue
            j += 1

    return benchmarks


def load_benchmarks():
    if not CATALOG_FILE.exists():
        print(f"Error: catalog not found at {CATALOG_FILE}")
        sys.exit(1)
    return parse_catalog(CATALOG_FILE)


def find_benchmark(benchmarks, bench_id):
    """Find a benchmark by ID (case-insensitive, partial match ok)."""
    bench_id = bench_id.upper()
    for b in benchmarks:
        if b.id.upper() == bench_id:
            return b
    # Partial match
    matches = [b for b in benchmarks if b.id.upper().startswith(bench_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Multiple matches for '{bench_id}': {[m.id for m in matches]}")
        sys.exit(1)
    print(f"Benchmark '{bench_id}' not found.")
    sys.exit(1)


def print_task(benchmark):
    """Print the benchmark task in a structured format."""
    print("=" * 72)
    print(f"  BENCHMARK: {benchmark.id} -- {benchmark.title}")
    print(f"  Category: {benchmark.category.upper()}  |  "
          f"Difficulty: {benchmark.difficulty}  |  "
          f"Responsible: {benchmark.responsible}")
    print("=" * 72)
    print(f"\n  TASK:")
    print(f"  {benchmark.description}")
    print(f"\n  SUCCESS CRITERIA:")
    for crit in benchmark.success_criteria.split(". "):
        crit = crit.strip().rstrip(".")
        if crit:
            print(f"    [PASS] {crit}")
    print(f"\n  FAILURE CRITERIA:")
    for crit in benchmark.failure_criteria.split(". "):
        crit = crit.strip().rstrip(".")
        if crit:
            print(f"    [FAIL] {crit}")
    print(f"\n  QUALITY AXES TO SCORE (1-5 each):")
    for axis in QUALITY_AXES:
        print(f"    * {axis}")
    print("\n" + "=" * 72)
    print("Execute the task, then run:")
    print(f"  python {__file__} --score {benchmark.id}")
    print("=" * 72)


def interactive_score(benchmark):
    """Interactive scoring for a completed benchmark."""
    print(f"\nScoring {benchmark.id} -- {benchmark.title}")
    print(f"Success criteria: {benchmark.success_criteria}")
    print(f"Failure criteria: {benchmark.failure_criteria}")
    print()

    outcome = input("Outcome (pass/fail): ").strip().lower()
    while outcome not in ("pass", "fail"):
        outcome = input("Enter 'pass' or 'fail': ").strip().lower()

    scores = {}
    print("\nRate each axis 1-5:")
    for axis in QUALITY_AXES:
        val = input(f"  {axis} (1-5): ").strip()
        while val not in ("1", "2", "3", "4", "5"):
            val = input(f"  {axis} (1-5): ").strip()
        scores[axis] = int(val)

    weaknesses = []
    print("\nEnter weaknesses (one per line, blank to finish):")
    while True:
        w = input("  > ").strip()
        if not w:
            break
        weaknesses.append(w)

    output_path = input("\nOutput file path (relative to outputs/): ").strip()
    duration_str = input("Duration (seconds): ").strip()
    tool_calls_str = input("Tool calls count: ").strip()

    result = {
        "result_id": f"{benchmark.id}-{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        "benchmark_id": benchmark.id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_type": benchmark.responsible,
        "task": benchmark.title,
        "execution": {
            "duration_s": int(duration_str) if duration_str else 0,
            "tool_calls": int(tool_calls_str) if tool_calls_str else 0,
            "outcome": outcome,
            "output_path": str(OUTPUTS_DIR / output_path) if output_path else ""
        },
        "scores": {
            **scores,
            "average": sum(scores.values()) / len(scores)
        },
        "pass_criteria": {
            "compiles": True,
            "tests_pass": outcome == "pass",
            "no_new_deps": True,
            "follows_style": True
        },
        "weaknesses": weaknesses,
        "trace_ref": f"trace-{datetime.now(timezone.utc).strftime('%Y%m%d')}-bench-{benchmark.id.lower()}"
    }

    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_file = RESULTS_DIR / f"{benchmark.id}-{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Result saved to {result_file}")
    update_summary()
    return result


def _benchmark_category(benchmark_id):
    """Map BENCH-X-NNN format to category name."""
    cat_map = {"r": "research", "c": "coding", "p": "planning", "o": "operational"}
    letter = benchmark_id.split("-")[1].lower() if "-" in benchmark_id else ""
    return cat_map.get(letter, "unknown")


def update_summary():
    """Regenerate the summary dashboard."""
    results = list(RESULTS_DIR.glob("BENCH-*.json"))
    summary_file = RESULTS_DIR / "summary.json"

    total = len(results)
    passed = 0
    failed = 0
    all_scores = {"research": [], "coding": [], "planning": [], "operational": []}
    all_weaknesses = []

    for rf in results:
        try:
            with open(rf, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("execution", {}).get("outcome") == "pass":
                passed += 1
            else:
                failed += 1
            cat = _benchmark_category(data.get("benchmark_id", ""))
            avg = data.get("scores", {}).get("average")
            if avg and cat in all_scores:
                all_scores[cat].append(avg)
            all_weaknesses.extend(data.get("weaknesses", []))
        except (json.JSONDecodeError, KeyError):
            pass

    summary = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "total_benchmarks": total,
        "completed": total,
        "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        "passed": passed,
        "failed": failed,
        "avg_scores": {
            cat: round(sum(vals) / len(vals), 2) if vals else 0.0
            for cat, vals in all_scores.items()
        },
        "weaknesses": all_weaknesses[:20],
        "weakness_count": len(all_weaknesses)
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Summary updated: {total}/{len(results)} benchmarks, "
          f"{passed} pass, {failed} fail, "
          f"{len(all_weaknesses)} weaknesses")


def print_summary():
    """Print the current summary from disk."""
    if not SUMMARY_FILE.exists():
        print("No summary yet. Run some benchmarks first.")
        return
    with open(SUMMARY_FILE, encoding="utf-8") as f:
        summary = json.load(f)
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Self-harness Benchmark Runner")
    parser.add_argument("benchmark", nargs="?", help="Benchmark ID (e.g. BENCH-R-01)")
    parser.add_argument("--all", action="store_true", help="List all benchmarks")
    parser.add_argument("--category", help="Filter by category (research, coding, planning, operational)")
    parser.add_argument("--score", action="store_true", help="Score a completed benchmark (interactive)")
    parser.add_argument("--dry-run", action="store_true", help="Preview task without executing")
    parser.add_argument("--summary", action="store_true", help="Show summary dashboard")
    parser.add_argument("--json", action="store_true", help="JSON output for listing")
    parser.add_argument("--stats", action="store_true", help="Show aggregate statistics across all benchmarks")
    parser.add_argument("--validate", metavar="RESULT_FILE",
                        help="Export blind validation prompt from result JSON (e.g. results/BENCH-R-01-20260708.json)")
    parser.add_argument("--import-validation", nargs=2, metavar=("RESULT", "RESPONSE"),
                        help="Import GPT validation response into result JSON")

    args = parser.parse_args()
    benchmarks = load_benchmarks()

    # Summary
    if args.summary:
        print_summary()
        return

    # Stats
    if args.stats:
        from utils import compute_aggregate_stats
        stats = compute_aggregate_stats(RESULTS_DIR)
        print(f"\n{'='*50}")
        print(f"  BENCHMARK AGGREGATE STATISTICS")
        print(f"{'='*50}")
        print(f"  Total benchmarks: {stats['total_benchmarks']}")
        print(f"  Average score:    {stats['avg_score']:.2f}")
        print(f"  Highest:          {stats['highest']['id']} ({stats['highest']['score']:.2f})")
        print(f"  Lowest:           {stats['lowest']['id']} ({stats['lowest']['score']:.2f})")
        print(f"  Pass rate:        {stats['pass_rate']}%")
        print(f"\n  Category breakdown:")
        for cat in stats["category_breakdown"]:
            print(f"    {cat['category']:12s} {cat['count']:2d} benchmarks, "
                  f"avg score {cat['avg_score']:.2f}, avg duration {cat['avg_duration']:.0f}s")
        print(f"{'='*50}\n")
        return

    # List all or by category
    if args.all or args.category:
        filtered = benchmarks
        if args.category:
            filtered = [b for b in benchmarks if b.category == args.category.lower()]
        if args.json:
            print(json.dumps([
                {"id": b.id, "title": b.title, "category": b.category,
                 "difficulty": b.difficulty, "responsible": b.responsible}
                for b in filtered
            ], indent=2))
        else:
            print(f"\n{'ID':<15} {'Title':<35} {'Cat':<6} {'Diff':<8} {'Resp'}")
            print("-" * 80)
            for b in filtered:
                print(f"{b.id:<15} {b.title:<35} {b.category.upper():<6} "
                      f"{b.difficulty:<8} {b.responsible}")
            print(f"\nTotal: {len(filtered)} benchmarks")
        return

    # Score mode
    if args.score:
        if not args.benchmark:
            print("Error: --score requires a benchmark ID")
            sys.exit(1)
        bench = find_benchmark(benchmarks, args.benchmark)
        interactive_score(bench)
        return

    # Dry run
    if args.dry_run:
        if not args.benchmark:
            print("Error: --dry-run requires a benchmark ID")
            sys.exit(1)
        bench = find_benchmark(benchmarks, args.benchmark)
        print_task(bench)
        return

    # Validate
    if args.validate:
        from validator import export_validation_prompt
        export_validation_prompt(Path(args.validate))
        return

    # Import validation
    if args.import_validation:
        from validator import import_validation
        result_path, response_path = args.import_validation
        val = import_validation(Path(result_path), Path(response_path))
        if val:
            bid = Path(result_path).stem
            print(f"\nValidation imported for {bid}:")
            print(f"  Executor avg: {val['executor_average']}")
            print(f"  GPT avg:      {val['gpt_average']}")
            print(f"  Divergence:   {val['overall_divergence']}")
            if val.get('overall_divergence', 0) > 1.5:
                print(f"  *** FLAGGED: divergence > 1.5 ***")
            print(f"  GPT verdict:  {val.get('gpt_verdict', '?')}")
        return

    # Run single benchmark
    if args.benchmark:
        bench = find_benchmark(benchmarks, args.benchmark)
        print_task(bench)
        return

    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
