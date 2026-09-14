"""BENCH-O-01: State Report for benchmarks directory."""
from pathlib import Path
import json

d = Path(r"C:\Users\think\AppData\Local\Temp\self-harness-sync\benchmarks")
results_dir = d / "results"
outputs_dir = d / "outputs"
summary_file = results_dir / "summary.json"
sum_data = json.loads(summary_file.read_text(encoding="utf-8"))

results = sorted(results_dir.glob("BENCH-*.json"))
outputs = sorted(outputs_dir.glob("*.txt"))

print("=== BENCH-O-01: Benchmark Runner State Report ===")
print("Timestamp: 2026-07-08")
print()
print("== Runner ==")
run_lines = len((d / "run.py").read_text().splitlines())
score_lines = len((d / "score.py").read_text().splitlines())
print(f"  run.py:   {(d / 'run.py').stat().st_size:>5} bytes, {run_lines} lines")
print(f"  score.py: {(d / 'score.py').stat().st_size:>5} bytes, {score_lines} lines")
print()
print("== Results ==")
print(f"  Completed:  {sum_data['completed']}/20")
print(f"  Pass rate:  {sum_data['pass_rate']}% ({sum_data['passed']} pass, {sum_data['failed']} fail)")
print(f"  Avg scores: {sum_data['avg_scores']}")
print(f"  Weaknesses: {sum_data['weakness_count']}")
print()
print(f"  {'ID':12s} {'Score':6s} {'Outcome':8s} {'Duration':8s}")
print(f"  {'-'*12} {'-'*6} {'-'*8} {'-'*8}")
for rf in results:
    j = json.loads(rf.read_text(encoding="utf-8"))
    bid = j["benchmark_id"]
    avg = j["scores"]["average"]
    out = j["execution"]["outcome"]
    dur = j["execution"]["duration_s"]
    print(f"  {bid:12s} {avg:<6.2f} {out:<8s} {dur:<8d}")
print()
print("== Outputs ==")
for o in outputs:
    print(f"  {o.name:30s} {o.stat().st_size:>6,} bytes")
print()
print("== Summary ==")
print(f"  summary.json: {summary_file.stat().st_size:,} bytes")
print(f"  last_updated: {sum_data['last_updated']}")
