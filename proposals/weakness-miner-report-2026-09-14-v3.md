# Weakness Miner Report

**Generated:** 2026-09-14T06:50:14.887449+00:00Z
**Source:** comparison_report.md

## Summary

- Total benchmarks: 20
- Flagged benchmarks (diff > 1.5): 3
- Average executor/validator diff: 0.69
- Agreement rate (diff ≤ 1.0): 75%
- Failure records analyzed: 82

## Flagged Benchmarks

| Benchmark | Exec Avg | GPT Avg | Diff |
|-----------|----------|---------|------|
| BENCH-O-04 | 5.00 | 2.62 | 2.38 |
| BENCH-O-05 | 4.88 | 2.75 | 2.13 |
| BENCH-P-04 | 5.00 | 3.12 | 1.88 |

## Weakness Themes

### 1. Low faithfulness scores on coding/operational outputs (priority: high)

- **Evidence:** Large exec-gpt gap on faithfulness axis indicates outputs may not follow constraints precisely.
- **Benchmarks:** BENCH-O-04, BENCH-O-05, BENCH-P-04

### 2. Outputs score high on actionability internally but low externally (priority: medium)

- **Evidence:** Validator finds outputs not directly usable despite executor passing them.
- **Benchmarks:** BENCH-O-04, BENCH-O-05

### 3. Recurring failure categories in backlog (priority: medium)

- **Evidence:** Top failure categories across 82 records.
- **Top categories:** external (9), process (9), tool (8)

## Ranked Improvement Candidates

| Rank | Candidate | Score | Priority |
|------|-----------|-------|----------|
| 1 | Low faithfulness scores on coding/operational outputs | 6 | high |
| 2 | Outputs score high on actionability internally but low externally | 4 | medium |
| 3 | Recurring failure categories in backlog | 2 | medium |

## Proposed Next Steps

1. File a formal harness improvement proposal for: **Low faithfulness scores on coding/operational outputs**
2. Verify using benchmarks: BENCH-O-04, BENCH-O-05, BENCH-P-04
3. Implement the change in a feature branch.
4. Run `tools/revalidate_benchmarks.py` and check that diff drops.
