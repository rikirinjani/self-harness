#!/usr/bin/env python3
"""Generate per-benchmark validation prompts for blind GPT evaluation.

Usage:
    python validator/generate_prompts.py          # Generate all 20
    python validator/generate_prompts.py BENCH-R  # Filter by prefix
    python validator/generate_prompts.py --list    # List what would be generated

Output: validator/prompts/BENCH-X-NN.txt (one file per benchmark)
"""

import json
import re
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BENCHMARKS_DIR = THIS_DIR.parent / "benchmarks"
CATALOG_FILE = BENCHMARKS_DIR.parent / "benchmark_catalog.md"
RESULTS_DIR = BENCHMARKS_DIR / "results"
OUTPUTS_DIR = BENCHMARKS_DIR / "outputs"
PROMPTS_DIR = THIS_DIR / "prompts"

QUALITY_AXES = [
    ("correctness", "Is the output factually/technically correct?"),
    ("completeness", "Does it cover all required aspects?"),
    ("clarity", "Is the output clear and well-structured?"),
    ("reasoning", "Is the logic/reasoning sound?"),
    ("precision", "Is it specific and precise vs vague?"),
    ("efficiency", "Is the approach efficient?"),
    ("actionability", "Can the output be acted upon directly?"),
    ("faithfulness", "Does it stay within scope without hallucinating?"),
]


def load_catalog():
    """Load benchmarks from catalog by importing run.py's parser."""
    sys.path.insert(0, str(BENCHMARKS_DIR))
    from run import parse_catalog
    raw = parse_catalog(CATALOG_FILE)
    benchmarks = {}
    cat_map = {"R": "research", "C": "coding", "P": "planning", "O": "operational"}
    for b in raw:
        letter = b.id.split("-")[1].upper()
        cat_short = {"R": "RES", "C": "COD", "P": "PLN", "O": "OPS"}.get(letter, "?")
        benchmarks[b.id] = {
            "id": b.id,
            "title": b.title,
            "letter": letter,
            "category": cat_short,
            "description": b.description,
            "success": b.success_criteria,
            "failure": b.failure_criteria,
            "difficulty": b.difficulty,
        }
    return benchmarks


def find_output(bench_id):
    """Find the output file for a benchmark."""
    # Known output locations (where we saved them during Phase 2 execution)
    known = {
        "BENCH-C-01": BENCHMARKS_DIR / "utils.py",
        "BENCH-C-02": OUTPUTS_DIR / "test_C02_bug.py",
        "BENCH-C-03": None,  # refactor has no separate output (changes were in run.py)
        "BENCH-C-04": OUTPUTS_DIR / "test_C04_stats.py",
        "BENCH-C-05": BENCHMARKS_DIR / "phase2_report.py",
        "BENCH-O-04": OUTPUTS_DIR / "BENCH-O-04.txt",  # might not have been created
        "BENCH-R-01": None,  # interactive — no file saved
    }
    result = known.get(bench_id)
    if result and result.exists():
        return result

    letter = bench_id.split("-")[1]
    number = bench_id.split("-")[2]
    for ext in [".txt", ".py", ".md"]:
        f = OUTPUTS_DIR / f"{bench_id}{ext}"
        if f.exists():
            return f
    for f in OUTPUTS_DIR.glob(f"{bench_id}*"):
        return f
    for f in OUTPUTS_DIR.glob(f"{letter}-{number}*"):
        return f
    return None


def generate_prompt(bench):
    """Generate a single blind-evaluation prompt."""
    bench_id = bench["id"]
    desc = bench.get("description", "No description available")
    success = bench.get("success", "No criteria specified")
    failure = bench.get("failure", "No criteria specified")
    diff = bench.get("difficulty", "?")
    cat = bench.get("category", "?")

    # Find output
    out_file = find_output(bench_id)
    output_text = ""
    if out_file and out_file.exists():
        try:
            output_text = out_file.read_text(encoding="utf-8")
            if len(output_text) > 8000:
                # Keep first 3000 and last 3000 if too long
                output_text = output_text[:3000] + "\n\n[...truncated...]\n\n" + output_text[-3000:]
        except Exception:
            output_text = "[Error reading output file]"
    else:
        output_text = "[No output file found — benchmark was executed directly in agent session]"

    prompt = f"""\
=== BENCHMARK VALIDATION ===

Benchmark: {bench_id} ({cat})
Title: {bench['title']}
Difficulty: {diff}

TASK DESCRIPTION:
{desc}

SUCCESS CRITERIA:
{success}

FAILURE CRITERIA:
{failure}

=== AGENT OUTPUT ===

{output_text}

=== EVALUATION ===

Please score this benchmark output on each of the 8 quality axes below.
Use the following scale:
  5 = Excellent — exceeds expectations
  4 = Good — meets criteria with minor room for improvement
  3 = Adequate — meets minimum bar
  2 = Poor — significant gaps
  1 = Failing — does not meet criteria

SCORING:

1. correctness (1-5): ___
   note: ____

2. completeness (1-5): ___
   note: ____

3. clarity (1-5): ___
   note: ____

4. reasoning (1-5): ___
   note: ____

5. precision (1-5): ___
   note: ____

6. efficiency (1-5): ___
   note: ____

7. actionability (1-5): ___
   note: ____

8. faithfulness (1-5): ___
   note: ____

WEAKNESSES (list specific issues, be critical):
1. ____
2. ____
3. ____

STRENGTHS (what was done well):
1. ____
2. ____

OVERALL VERDICT: Pass / Fail
"""
    return prompt


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filter", nargs="?", help="Optional prefix filter (e.g. BENCH-R)")
    parser.add_argument("--list", action="store_true", help="List benchmarks without generating")
    args = parser.parse_args()

    catalog = load_catalog()
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    bench_ids = sorted(catalog.keys())
    if args.filter:
        bench_ids = [b for b in bench_ids if b.startswith(args.filter.upper())]

    if not bench_ids:
        print(f"No benchmarks found matching '{args.filter}'")
        sys.exit(1)

    if args.list:
        print("Benchmarks ready for validation:")
        for bid in bench_ids:
            b = catalog[bid]
            out = find_output(bid)
            has_output = "[OUTPUT]" if out and out.exists() else "[no output]"
            print(f"  {bid:14s} {b.get('category', '?'):3s}  {has_output}")
        print(f"\nTotal: {len(bench_ids)}")
        return

    count = 0
    for bid in bench_ids:
        prompt = generate_prompt(catalog[bid])
        prompt_file = PROMPTS_DIR / f"{bid}.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        count += 1
        print(f"  [OK] {prompt_file.name}")

    print(f"\nGenerated {count} validation prompts in {PROMPTS_DIR}")


if __name__ == "__main__":
    main()
