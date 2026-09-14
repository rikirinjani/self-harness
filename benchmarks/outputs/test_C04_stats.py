"""BENCH-C-04: Multi-File Feature Test — --stats flag.

Tests:
1. compute_aggregate_stats returns expected structure
2. --stats CLI works (integration smoke test)
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils import compute_aggregate_stats

results_dir = Path(__file__).resolve().parent.parent / "results"
stats = compute_aggregate_stats(results_dir)

# Test 1: Structure
assert isinstance(stats, dict), "stats should be a dict"
assert "total_benchmarks" in stats
assert "avg_score" in stats
assert "highest" in stats
assert "lowest" in stats
assert "pass_rate" in stats
assert "category_breakdown" in stats
print("[PASS] Structure: all keys present")

# Test 2: Types
assert isinstance(stats["total_benchmarks"], int)
assert isinstance(stats["avg_score"], float)
assert isinstance(stats["highest"], dict)
assert isinstance(stats["lowest"], dict)
assert isinstance(stats["pass_rate"], float)
assert isinstance(stats["category_breakdown"], list)
assert len(stats["category_breakdown"]) == 4
print("[PASS] Types: correct")

# Test 3: Consistency
assert stats["total_benchmarks"] > 0, "at least one benchmark"
assert stats["highest"]["score"] >= stats["lowest"]["score"]
assert 0 <= stats["pass_rate"] <= 100
assert len(stats["category_breakdown"]) == 4
print("[PASS] Consistency: highest >= lowest, pass_rate in range")

# Test 4: Category breakdown has expected fields
for cat in stats["category_breakdown"]:
    assert "category" in cat
    assert "count" in cat
    assert "avg_score" in cat
    assert "avg_duration" in cat
print("[PASS] Category breakdown structure")

# Test 5: Smoke test — CLI runs without error
import subprocess
result = subprocess.run(
    [sys.executable, str(Path(__file__).resolve().parent.parent / "run.py"), "--stats"],
    capture_output=True, text=True
)
assert result.returncode == 0, f"CLI exited with {result.returncode}"
assert "BENCHMARK AGGREGATE STATISTICS" in result.stdout
print("[PASS] CLI --stats smoke test")

print(f"\nAll 5 tests passed ({stats['total_benchmarks']} benchmarks)")
