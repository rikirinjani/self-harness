#!/usr/bin/env python3
"""Non-interactive benchmark score recorder. Called by the agent after benchmark execution.

Usage:
    python benchmarks/score.py BENCH-R-01 pass \\
        --correctness 5 --completeness 5 --clarity 5 \\
        --reasoning 5 --precision 5 --efficiency 5 \\
        --actionability 5 --faithfulness 5 \\
        --weaknesses "note 1" --weaknesses "note 2" \\
        --duration 30 --tool-calls 5 --output R-01.txt
"""
import argparse
import json
import sys
from datetime import datetime, timezone

# Reconfigure stdout to UTF-8 for Unicode support on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))
from run import load_benchmarks, find_benchmark, QUALITY_AXES, RESULTS_DIR, OUTPUTS_DIR, update_summary


def main():
    parser = argparse.ArgumentParser(description="Score a completed benchmark")
    parser.add_argument("benchmark_id", help="Benchmark ID (e.g. BENCH-R-01)")
    parser.add_argument("outcome", choices=["pass", "fail"], help="Overall outcome")
    parser.add_argument("--correctness", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--completeness", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--clarity", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--reasoning", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--precision", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--efficiency", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--actionability", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--faithfulness", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--weaknesses", action="append", default=[])
    parser.add_argument("--duration", type=int, default=0)
    parser.add_argument("--tool-calls", type=int, default=0)
    parser.add_argument("--output", default="output.txt")

    args = parser.parse_args()
    benches = load_benchmarks()
    b = find_benchmark(benches, args.benchmark_id)

    scores = {ax: getattr(args, ax) for ax in QUALITY_AXES}
    scores["average"] = round(sum(scores.values()) / len(scores), 2)

    now = datetime.now(timezone.utc)
    result = {
        "result_id": f"{b.id}-{now.strftime('%Y%m%d')}",
        "benchmark_id": b.id,
        "timestamp": now.isoformat(),
        "agent_type": b.responsible,
        "task": b.title,
        "execution": {
            "duration_s": args.duration,
            "tool_calls": args.tool_calls,
            "outcome": args.outcome,
            "output_path": str(OUTPUTS_DIR / args.output)
        },
        "scores": scores,
        "pass_criteria": {
            "compiles": True,
            "tests_pass": args.outcome == "pass",
            "no_new_deps": True,
            "follows_style": True
        },
        "weaknesses": args.weaknesses,
        "trace_ref": f"trace-{now.strftime('%Y%m%d')}-bench-{b.id.lower()}"
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    result_file = RESULTS_DIR / f"{b.id}-{now.strftime('%Y%m%d')}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[OK] Saved {b.id} to {result_file}")
    update_summary()
    write_trace(b, args, now, result)


def write_trace(benchmark, args, now, result):
    """Write trace and optional failure record to central self-harness."""
    from uuid import uuid4
    trace_dir = Path.home() / "self-harness" / "traces"
    fail_dir = Path.home() / "self-harness" / "failures"
    ts = now.strftime("%Y%m%dT%H%M%S")
    trace_id = str(uuid4())

    trace = {
        "trace_id": trace_id,
        "timestamp": now.isoformat(),
        "agent": "benchmark-runner",
        "task_description": f"Benchmark {benchmark.id}: {benchmark.title}",
        "outcome": args.outcome,
        "duration_s": args.duration,
        "tool_calls": args.tool_calls,
        "key_files": [result.get("execution", {}).get("output_path", "")],
        "result_ref": result.get("result_id", ""),
        "benchmark_id": benchmark.id,
        "scores": result.get("scores", {}),
        "weaknesses": args.weaknesses,
    }

    # Write trace
    trace_dir.mkdir(parents=True, exist_ok=True)
    trace_file = trace_dir / f"{ts}-bench-{benchmark.id.lower()}.json"
    with open(trace_file, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
    print(f"[TRACE] Written to {trace_file}")

    # Write failure if outcome is fail
    if args.outcome == "fail":
        fail_dir.mkdir(parents=True, exist_ok=True)
        failure = {
            "trace_id": trace_id,
            "timestamp": now.isoformat(),
            "category": "benchmark",
            "agent": "benchmark-runner",
            "trigger": "benchmark_failure",
            "severity": "major",
            "description": f"Benchmark {benchmark.id} failed",
            "root_cause": "; ".join(args.weaknesses) if args.weaknesses else "Unknown",
            "status": "open",
            "trace_ref": trace_file.name,
            "result_ref": result.get("result_id", ""),
        }
        fail_file = fail_dir / f"{ts}-bench-{benchmark.id.lower()}.json"
        with open(fail_file, "w", encoding="utf-8") as f:
            json.dump(failure, f, indent=2, ensure_ascii=False)
        print(f"[FAIL] Written to {fail_file}")


if __name__ == "__main__":
    main()
