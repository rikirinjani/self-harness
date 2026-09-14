"""BENCH-C-02: Bug Fix Test — total_benchmarks should not be hardcoded.

Existing behavior: summary.json reports total_benchmarks=20 even when
only 15 result files exist. This inflates completion % artificially.

Expected: total_benchmarks should equal len(result_files).
"""
import json
from pathlib import Path

# Read summary
results_dir = Path(__file__).resolve().parent.parent / "results"
summary_file = results_dir / "summary.json"
summary = json.loads(summary_file.read_text(encoding="utf-8"))

# Count actual result files
result_files = list(results_dir.glob("BENCH-*.json"))
# Exclude summary.json itself
result_files = [f for f in result_files if f.name != "summary.json"]

actual_count = len(result_files)
reported_total = summary["total_benchmarks"]
completed = summary["completed"]

print(f"Result files found: {actual_count}")
print(f"Reported total_benchmarks: {reported_total}")
print(f"Completed: {completed}")

# This should fail before bug fix
assert reported_total == actual_count, (
    f"BUG: total_benchmarks={reported_total} is hardcoded, "
    f"but actual result files count = {actual_count}."
)

print("[PASS] total_benchmarks matches actual result file count")
