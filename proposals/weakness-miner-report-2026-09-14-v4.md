# Weakness Miner Report

**Generated:** 2026-09-14T07:12:13.729958+00:00Z
**Sources:** benchmark comparison, failure records, trace metadata

## Summary

- Total benchmarks: 20
- Flagged benchmarks (diff > 1.5): 3
- Average executor/validator diff: 0.69
- Agreement rate (diff ≤ 1.0): 75%
- Failure records analyzed: 82
- Trace records analyzed: 1771
- Evidence sources: benchmark, failure, trace

## Flagged Benchmarks

| Benchmark | Exec Avg | GPT Avg | Diff |
|-----------|----------|---------|------|
| BENCH-O-04 | 5.00 | 2.62 | 2.38 |
| BENCH-O-05 | 4.88 | 2.75 | 2.13 |
| BENCH-P-04 | 5.00 | 3.12 | 1.88 |

## Weakness Themes

### 1. Low correctness scores on flagged benchmarks (source: benchmark, priority: high)

- **Evidence:** Large exec-gpt gap on correctness axis.
- **Benchmarks:** BENCH-O-04, BENCH-O-05, BENCH-P-04
- **Axes most affected:** correctness

### 2. Low completeness scores on flagged benchmarks (source: benchmark, priority: medium)

- **Evidence:** Large exec-gpt gap on completeness axis.
- **Benchmarks:** BENCH-O-04, BENCH-O-05
- **Axes most affected:** completeness

### 3. Low precision scores on flagged benchmarks (source: benchmark, priority: medium)

- **Evidence:** Large exec-gpt gap on precision axis.
- **Benchmarks:** BENCH-O-04, BENCH-O-05, BENCH-P-04
- **Axes most affected:** precision

### 4. Low actionability scores on flagged benchmarks (source: benchmark, priority: medium)

- **Evidence:** Large exec-gpt gap on actionability axis.
- **Benchmarks:** BENCH-O-04, BENCH-O-05
- **Axes most affected:** actionability

### 5. Low faithfulness scores on flagged benchmarks (source: benchmark, priority: high)

- **Evidence:** Large exec-gpt gap on faithfulness axis.
- **Benchmarks:** BENCH-O-04, BENCH-O-05, BENCH-P-04
- **Axes most affected:** faithfulness

### 6. Recurring failure categories in backlog (source: failure, priority: high)

- **Evidence:** Top failure categories across 82 records.
- **Top categories:** external (9), process (9), tool (8), architecture (8), unknown (5)

### 7. Most active agents in trace corpus (source: trace, priority: low)

- **Evidence:** Trace activity distribution across 1771 records.
- **Agents:** orchestrator (945), fixer (182), coordinator (178), librarian (119), explorer (119)

## Ranked Improvement Candidates

| Rank | Candidate | Score | Priority | Source |
|------|-----------|-------|----------|--------|
| 1 | Recurring failure categories in backlog | 8 | high | failure |
| 2 | Low correctness scores on flagged benchmarks | 6 | high | benchmark |
| 3 | Low faithfulness scores on flagged benchmarks | 6 | high | benchmark |
| 4 | Most active agents in trace corpus | 6 | low | trace |
| 5 | Low precision scores on flagged benchmarks | 5 | medium | benchmark |
| 6 | Low completeness scores on flagged benchmarks | 4 | medium | benchmark |
| 7 | Low actionability scores on flagged benchmarks | 4 | medium | benchmark |

## Proposed Next Steps

1. Generate a formal harness improvement proposal for: **Recurring failure categories in backlog**
2. Verify using benchmarks: TBD
3. Implement the change in a feature branch.
4. Run `tools/revalidate_benchmarks.py` and check that diff drops.
