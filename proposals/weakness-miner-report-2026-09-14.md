# Weakness Miner Report

**Generated:** 2026-09-14T05:52:17.260938+00:00Z
**Source:** comparison_report.md

## Summary

- Total benchmarks: 20
- Flagged benchmarks (diff > 1.5): 8
- Average executor/validator diff: 1.40
- Agreement rate (diff ≤ 1.0): 50%
- Failure records analyzed: 82

## Flagged Benchmarks

| Benchmark | Exec Avg | GPT Avg | Diff |
|-----------|----------|---------|------|
| BENCH-C-01 | 5.00 | 3.12 | 1.88 |
| BENCH-C-02 | 5.00 | 2.12 | 2.88 |
| BENCH-C-03 | 5.00 | 1.00 | 4.00 |
| BENCH-C-04 | 4.88 | 2.00 | 2.88 |
| BENCH-O-04 | 5.00 | 2.62 | 2.38 |
| BENCH-O-05 | 4.88 | 2.75 | 2.13 |
| BENCH-P-04 | 5.00 | 3.12 | 1.88 |
| BENCH-R-01 | 4.88 | 1.00 | 3.88 |

## Weakness Themes

### 1. Executor score inflation on coding benchmarks (priority: high)

- **Evidence:** GPT validator frequently marks coding outputs fail while executor marks pass.
- **Benchmarks:** BENCH-C-01, BENCH-C-02, BENCH-C-03, BENCH-C-04, BENCH-C-05
- **Axes most affected:** correctness, actionability, faithfulness

### 2. Benchmarks producing outputs the validator rejects outright (priority: high)

- **Evidence:** GPT validator avg < 2.0 suggests outputs miss core requirements.
- **Benchmarks:** BENCH-C-03, BENCH-R-01

### 3. Low faithfulness scores on coding/operational outputs (priority: high)

- **Evidence:** Large exec-gpt gap on faithfulness axis indicates outputs may not follow constraints precisely.
- **Benchmarks:** BENCH-C-01, BENCH-C-02, BENCH-C-03, BENCH-C-04, BENCH-O-04, BENCH-O-05, BENCH-P-04, BENCH-R-01

### 4. Outputs score high on actionability internally but low externally (priority: medium)

- **Evidence:** Validator finds outputs not directly usable despite executor passing them.
- **Benchmarks:** BENCH-C-02, BENCH-C-03, BENCH-C-04, BENCH-O-04, BENCH-O-05, BENCH-R-01

### 5. Recurring failure categories in backlog (priority: medium)

- **Evidence:** Top failure categories across 82 records.
- **Top categories:** external (9), process (9), tool (8)

## Ranked Improvement Candidates

| Rank | Candidate | Score | Priority |
|------|-----------|-------|----------|
| 1 | Low faithfulness scores on coding/operational outputs | 11 | high |
| 2 | Executor score inflation on coding benchmarks | 10.4 | high |
| 3 | Outputs score high on actionability internally but low externally | 8 | medium |
| 4 | Benchmarks producing outputs the validator rejects outright | 5 | high |
| 5 | Recurring failure categories in backlog | 2 | medium |

## Proposed Next Steps

1. File a formal harness improvement proposal for: **Low faithfulness scores on coding/operational outputs**
2. Verify using benchmarks: BENCH-C-01, BENCH-C-02, BENCH-C-03
3. Implement the change in a feature branch.
4. Run `tools/revalidate_benchmarks.py` and check that diff drops.
