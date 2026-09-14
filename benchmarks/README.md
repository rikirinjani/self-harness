# Benchmark Runner

Scripts and configuration for executing the Self-Harness benchmark suite.

## Files

- `runner.sh` — Main benchmark runner script (Phase 2)
- `baseline.json` — Baseline benchmark results (generated during Phase 2)

## Usage

```bash
./runner.sh --suite all --harness current
./runner.sh --suite BENCH-C --harness proposal-001
./runner.sh --compare baseline.json proposal-001-results.json
```

## Status

Phase 2 — not yet active.
