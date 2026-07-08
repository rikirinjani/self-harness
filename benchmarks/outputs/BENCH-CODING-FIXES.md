# Coding Benchmarks — Fixed + Resubmitted for Re-evaluation

## BENCH-C-01: Bounded Implementation (utils.py)
**What was fixed:**
- Added `title` field to highest/lowest dicts (was missing per spec)
- Added type hints to function signature: `results_dir: Path -> dict`
- Added detailed docstring explaining schema assumptions
- Empty-result case now returns `title: ""` for consistency

## BENCH-C-02: Bug Fix (run.py total_benchmarks)
**What was fixed:**
- Changed `total_benchmarks: 20` to `total_benchmarks: total` (actual count)
- Fixed 2 additional encoding bugs discovered during regression check
- Test proves total now matches actual file count

## BENCH-C-03: Refactor for Clarity (run.py update_summary)
**What was fixed:**
- Extracted `_benchmark_category()` helper function
- Removed redundant `completed` variable (=same as `total`)
- Moved cat_map outside the loop
- Fixed cosmetic print hardcode

## BENCH-C-04: Multi-File Feature (--stats flag)
**What was fixed:**
- Added `--stats` flag to run.py argparse + handler
- Uses utils.compute_aggregate_stats() for data
- Touches 3 files: run.py, utils.py, test_C04_stats.py
- All 5 tests pass

## BENCH-C-05: Scripting (phase2_report.py)
**What was fixed:**
- Removed hardcoded `total_expected=20` -> reads catalog dynamically
- Fixed trace_ref check: `all()` on empty list no longer returns True
- Removed unused OUTPUTS_DIR constant

---

**Status:** All fixes applied and verified. Ready for GPT re-evaluation.
