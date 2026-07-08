# Phase 2 Plan: Benchmark Runner

**Prerequisite:** Phase 1 complete (177 traces, 44 failures, 9 categories — exit criteria exceeded 2026-07-08)
**Entry target:** Benchmark runner script executes 20/20 benchmarks, produces structured results
**Duration estimate:** ~1 week

---

## What Phase 2 Builds

A benchmark runner that executes the 20 benchmarks from `benchmark_catalog.md`, scores results against the 8 quality axes (Constitution §2.1), and records structured results. This produces the ground-truth measurements that Phase 4 (Weakness Miner) needs.

## Deliverables

### 1. Benchmark Runner Script

A Python (or bash) script at `benchmarks/run.py` that:

```bash
# Run all benchmarks
python benchmarks/run.py --all

# Run specific benchmark
python benchmarks/run.py BENCH-C-01

# Run category
python benchmarks/run.py --category coding

# Output format
python benchmarks/run.py BENCH-R-01 --json
```

The runner should:
- Read benchmark spec from `benchmark_catalog.md`
- Execute the benchmark task against the agent system
- Record agent output (code, analysis, plan, etc.)
- Score against 8 quality axes (1-5 each)
- Write structured result to `benchmarks/results/{benchmark_id}-{timestamp}.json`
- Support `--dry-run` to preview without executing

### 2. Result Schema

File: `benchmarks/results/{benchmark_id}-{timestamp}.json`

```json
{
  "result_id": "BENCH-C-01-20260708",
  "benchmark_id": "BENCH-C-01",
  "timestamp": "2026-07-08T12:00:00Z",
  "agent_type": "fixer",
  "task": "Bounded Implementation",
  "execution": {
    "duration_s": 120,
    "tool_calls": 15,
    "outcome": "pass",
    "output_path": "benchmarks/outputs/BENCH-C-01/output.ts"
  },
  "scores": {
    "correctness": 5,
    "completeness": 4,
    "clarity": 4,
    "reasoning": 5,
    "precision": 4,
    "efficiency": 4,
    "actionability": 5,
    "faithfulness": 5,
    "average": 4.5
  },
  "pass_criteria": {
    "compiles": true,
    "tests_pass": true,
    "no_new_deps": true,
    "follows_style": true
  },
  "weaknesses": [
    "Completeness: missing edge case for empty input",
    "Precision: variable name `data` is too generic"
  ],
  "trace_ref": "trace-20260708-bench-c-01"
}
```

### 3. Results Summary Dashboard

File: `benchmarks/results/summary.json` — auto-generated after each run:

```json
{
  "last_updated": "2026-07-08",
  "total_benchmarks": 20,
  "completed": 0,
  "pass_rate": 0,
  "avg_scores": {
    "research": null,
    "coding": null,
    "planning": null,
    "operational": null
  },
  "weaknesses": []
}
```

### 4. Trace Integration

Every benchmark run must produce a trace record in `traces/`:
```
traces/{timestamp}-bench-{benchmark_id}.json
```

If the benchmark fails (doesn't compile, wrong output), also produce a failure record in `failures/`.

This ensures benchmark results feed directly into the improvement pipeline (Phase 4).

## Execution Strategy

### Step 1 — Build Runner Core
Create `benchmarks/run.py` with:
- Benchmark loader (reads catalog)
- Execution engine (runs agent with benchmark prompt)
- Result collector (captures output + timing)
- Score entry (records quality axes scores)

### Step 2 — Run Research Benchmarks (5)
Execute BENCH-R-01 through BENCH-R-05. These are read-only (no code changes), so low risk.

### Step 3 — Run Operational Benchmarks (5)
Execute BENCH-O-01 through BENCH-O-05. These are script/report tasks, no code changes to core system.

### Step 4 — Run Planning Benchmarks (5)
Execute BENCH-P-01 through BENCH-P-05. These produce analysis/plans, not executable code.

### Step 5 — Run Coding Benchmarks (5)
Execute BENCH-C-01 through BENCH-C-05. These modify code — use git worktrees or sandbox for isolation.

## Progress Tracking

| Metric | Target | Current |
|--------|--------|---------|
| Runner script built | Done | Pending |
| Research benchmarks executed | 5/5 | 0 |
| Coding benchmarks executed | 5/5 | 0 |
| Planning benchmarks executed | 5/5 | 0 |
| Operational benchmarks executed | 5/5 | 0 |
| Results recorded | 20/20 | 0 |
| Weaknesses identified | >0 | 0 |

Update these counts in `phases/phase-2-progress.md` as benchmarks execute.

## Phase-Out Gate

Phase 2 is complete when:

- [ ] Runner script exists at `benchmarks/run.py`
- [ ] All 20 benchmarks have been executed
- [ ] All results recorded in `benchmarks/results/`
- [ ] Summary dashboard populated
- [ ] ≥5 weaknesses identified across all benchmarks
- [ ] All results have trace references

When these pass → proceed to Phase 3 (Validator).

## Resources

- Benchmark definitions: `benchmark_catalog.md`
- Quality axes: Constitution §2.1
- Scoring rubric: Constitution §2.2 (Code, Analysis, Plans rubrics)
- Shipping threshold: Constitution §2.7
- Protected artifacts: Constitution §2.5
