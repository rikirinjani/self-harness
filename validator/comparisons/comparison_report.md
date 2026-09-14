# Score Comparison: Phase 2 Executor vs GPT Validator

Generated: 2026-09-14 13:50

| Benchmark | Axes Matched | Exec Avg | GPT Avg | Diff | Exec Verdict | GPT Verdict |
|-----------|-------------|----------|---------|------|--------------|-------------|
| BENCH-C-01 | 8/8 | 5.00 | 4.75 | 0.25 | pass | pass |
| BENCH-C-02 | 8/8 | 5.00 | 4.75 | 0.25 | pass | pass |
| BENCH-C-03 | 8/8 | 5.00 | 4.62 | 0.38 | pass | pass |
| BENCH-C-04 | 8/8 | 4.88 | 4.75 | 0.13 | pass | pass |
| BENCH-C-05 | 8/8 | 5.00 | 4.62 | 0.38 | pass | pass |
| BENCH-O-01 | 8/8 | 4.75 | 4.00 | 0.75 | pass | pass |
| BENCH-O-02 | 8/8 | 5.00 | 4.75 | 0.25 | pass | pass |
| BENCH-O-03 | 8/8 | 4.88 | 4.62 | 0.26 | pass | pass |
| BENCH-O-04 | 8/8 | 5.00 | 2.62 | 2.38 ⚠️ | pass | None |
| BENCH-O-05 | 8/8 | 4.88 | 2.75 | 2.13 ⚠️ | pass | None |
| BENCH-P-01 | 8/8 | 4.75 | 3.50 | 1.25 | pass | None |
| BENCH-P-02 | 8/8 | 4.88 | 4.75 | 0.13 | pass | None |
| BENCH-P-03 | 8/8 | 4.88 | 4.88 | 0.00 | pass | None |
| BENCH-P-04 | 8/8 | 5.00 | 3.12 | 1.88 ⚠️ | pass | None |
| BENCH-P-05 | 8/8 | 4.88 | 4.88 | 0.00 | pass | None |
| BENCH-R-01 | 8/8 | 4.88 | 4.62 | 0.26 | pass | pass |
| BENCH-R-02 | 8/8 | 4.88 | 4.38 | 0.50 | pass | None |
| BENCH-R-03 | 8/8 | 4.88 | 4.38 | 0.50 | pass | None |
| BENCH-R-04 | 8/8 | 4.88 | 4.00 | 0.88 | pass | None |
| BENCH-R-05 | 8/8 | 4.88 | 3.62 | 1.26 | pass | None |

**Overall:** Executor avg 4.91 vs GPT avg 4.22 (avg diff 0.69)
**Agreement rate (within ±1.0):** 75% (15/20)

## Flagged Benchmarks (diff > 1.5)

### BENCH-O-04 (diff=2.38)

| Axis | Executor | GPT |
|------|----------|-----|
| correctness | 5 | 2 |
| completeness | 5 | 2 |
| clarity | 5 | 4 |
| reasoning | 5 | 3 |
| precision | 5 | 2 |
| efficiency | 5 | 4 |
| actionability | 5 | 2 |
| faithfulness | 5 | 2 |

### BENCH-O-05 (diff=2.13)

| Axis | Executor | GPT |
|------|----------|-----|
| correctness | 5 | 2 |
| completeness | 5 | 2 |
| clarity | 5 | 5 |
| reasoning | 4 | 3 |
| precision | 5 | 2 |
| efficiency | 5 | 4 |
| actionability | 5 | 2 |
| faithfulness | 5 | 2 |

### BENCH-P-04 (diff=1.88)

| Axis | Executor | GPT |
|------|----------|-----|
| correctness | 5 | 2 |
| completeness | 5 | 4 |
| clarity | 5 | 5 |
| reasoning | 5 | 3 |
| precision | 5 | 2 |
| efficiency | 5 | 3 |
| actionability | 5 | 4 |
| faithfulness | 5 | 2 |
