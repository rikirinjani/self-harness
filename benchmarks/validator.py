#!/usr/bin/env python3
"""Validation integration for the benchmark runner.

Called by run.py --validate and --import-validation.
"""

import json
import re
import sys
from pathlib import Path

VALIDATOR_DIR = Path(__file__).resolve().parent.parent / "validator"
PROMPTS_DIR = VALIDATOR_DIR / "prompts"
QUALITY_AXES = [
    "correctness", "completeness", "clarity", "reasoning",
    "precision", "efficiency", "actionability", "faithfulness",
]


def export_validation_prompt(result_file):
    """Generate a blind evaluation prompt from a result JSON and its output file.

    Args:
        result_file: Path to a BENCH-X-NN.json result file.

    Returns:
        Path to the generated prompt file, or None on failure.
    """
    try:
        with open(result_file, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading result: {e}")
        return None

    bid = data.get("benchmark_id", "?")
    title = data.get("task", "?")
    cat = data.get("agent_type", "?")
    output_path = data.get("execution", {}).get("output_path", "")

    # Read the benchmark output
    output_text = ""
    if output_path:
        output_file = Path(output_path)
        if output_file.exists():
            output_text = output_file.read_text(encoding="utf-8")
            if len(output_text) > 8000:
                output_text = output_text[:3000] + "\n\n[...truncated...]\n\n" + output_text[-3000:]
        else:
            output_text = f"[Output file not found: {output_path}]"
    else:
        output_text = "[No output file recorded]"

    # Build prompt
    prompt = f"""=== BLIND BENCHMARK VALIDATION ===

Benchmark: {bid}
Title: {title}
Category: {cat}

=== AGENT OUTPUT ===

{output_text}

=== EVALUATION ===

Score each axis 1-5 (5=excellent, 3=adequate, 1=poor):

"""

    for i, ax in enumerate(QUALITY_AXES, 1):
        prompt += f"{i}. {ax} (1-5): ___\n   note: ____\n\n"

    prompt += """WEAKNESSES (list specific issues, be critical):
1. ____
2. ____
3. ____

STRENGTHS (what was done well):
1. ____

OVERALL VERDICT: Pass / Fail
"""

    # Write to validator/prompts/
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    prompt_file = PROMPTS_DIR / f"{bid}.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    print(f"Prompt saved to {prompt_file}")
    print(f"Copy this file content into your independent evaluator (GPT, etc.)")
    return prompt_file


def import_validation(result_file, response_file):
    """Parse a GPT response and store validation scores in the result JSON.

    Args:
        result_file: Path to BENCH-X-NN.json result file.
        response_file: Path to GPT response text file.

    Returns:
        dict with comparison data, or None on failure.
    """
    # Read result
    try:
        with open(result_file, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading result: {e}")
        return None

    # Read GPT response
    try:
        response_text = response_file.read_text(encoding="utf-8")
    except OSError as e:
        print(f"Error reading response: {e}")
        return None

    # Parse scores from response
    gpt_scores = {}
    for ax in QUALITY_AXES:
        pattern = rf"{re.escape(ax)}\s*\(1-5\):\s*(\d)"
        m = re.search(pattern, response_text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            if 1 <= val <= 5:
                gpt_scores[ax] = val
        if ax not in gpt_scores:
            gpt_scores[ax] = None

    gpt_avg = round(
        sum(v for v in gpt_scores.values() if v) / len(QUALITY_AXES), 2
    ) if any(gpt_scores.values()) else None

    # Extract executor scores
    exec_scores = {ax: data.get("scores", {}).get(ax) for ax in QUALITY_AXES}
    exec_avg = data.get("scores", {}).get("average")

    # Compute per-axis divergence
    axis_diff = {}
    for ax in QUALITY_AXES:
        ev = exec_scores.get(ax)
        gv = gpt_scores.get(ax)
        if ev is not None and gv is not None:
            axis_diff[ax] = round(abs(ev - gv), 1)
        else:
            axis_diff[ax] = None

    overall_diff = round(abs((exec_avg or 0) - (gpt_avg or 0)), 2)

    # Extract verdict
    verdict = None
    m = re.search(r"OVERALL VERDICT:\s*(Pass|Fail)", response_text, re.IGNORECASE)
    if m:
        verdict = m.group(1).lower()

    validation = {
        "gpt_scores": gpt_scores,
        "gpt_average": gpt_avg,
        "gpt_verdict": verdict,
        "executor_average": exec_avg,
        "axis_divergence": axis_diff,
        "overall_divergence": overall_diff,
        "response_file": str(response_file),
    }

    # Store in result JSON
    data["validation"] = validation
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return validation


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validation pipeline")
    parser.add_argument("--export", help="Export validation prompt from result file")
    parser.add_argument("--import-response", nargs=2, metavar=("RESULT", "RESPONSE"),
                        help="Import GPT response into result JSON")
    args = parser.parse_args()

    if args.export:
        export_validation_prompt(Path(args.export))

    if args.import_response:
        result_path = Path(args.import_response[0])
        response_path = Path(args.import_response[1])
        val = import_validation(result_path, response_path)
        if val:
            bid = result_path.stem
            print(f"\nValidation imported for {bid}:")
            print(f"  Executor avg: {val['executor_average']}")
            print(f"  GPT avg:      {val['gpt_average']}")
            print(f"  Divergence:   {val['overall_divergence']}")
            if val['overall_divergence'] > 1.5:
                print(f"  *** FLAGGED: divergence > 1.5 ***")
            print(f"  GPT verdict:  {val.get('gpt_verdict', '?')}")


if __name__ == "__main__":
    main()
