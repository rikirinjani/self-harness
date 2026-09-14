# Phase 3 Progress

**Status:** ACTIVE — restarted 2026-09-14  
**Goal:** Close executor/validator gap and implement ≥1 harness improvement.  

---

## Baseline (2026-09-14)

| Metric | Value |
|--------|------:|
| Executor average | 4.91 |
| GPT validator average | 3.51 |
| Average diff | 1.40 |
| Agreement rate (±1.0) | 0% |
| Flagged benchmarks (diff > 1.5) | 8 |

### Flagged set
- BENCH-C-01 (diff 1.88)
- BENCH-C-02 (diff 2.88)
- BENCH-C-03 (diff 4.00)
- BENCH-C-04 (diff 2.88)
- BENCH-O-04 (diff 2.38)
- BENCH-O-05 (diff 2.13)
- BENCH-P-04 (diff 1.88)
- BENCH-R-01 (diff 3.88)

---

## Cumulative Progress

| Date | Flagged count | Avg diff | Agreement rate | Proposals filed | Proposals merged | Notes |
|------|--------------:|---------:|---------------:|----------------:|-----------------:|-------|
| 2026-09-14 | 8 | 1.40 | 0% | 0 | 0 | Phase 3 restarted; assets located |
| 2026-09-14 | 7 | 1.22 | 55% | 3 | 1 | P-001 deployed; BENCH-C-03 diff 0.38 |
| 2026-09-14 | 3 | 0.69 | 75% | 3 | 3 | P-002/P-003 deployed; coding + R-01 gaps closed |

---

## Deliverable Checklist

- [x] Validator comparison report exists
- [x] Harness improvement proposal template (`proposals/TEMPLATE-harness-improvement.md`)
- [x] Weakness miner script (`tools/weakness_miner.py`)
- [x] Re-validation pipeline stub (`tools/revalidate_benchmarks.py`)
- [ ] Weakness miner produced ≥2 reports
- [ ] ≥3 proposals filed
- [ ] ≥1 proposal implemented and re-validated
- [ ] Avg diff ≤ 1.0
- [ ] Agreement rate ≥ 70%
- [ ] Human approves exit

---

## Proposals

| ID | Weakness | Status | Benchmark verification | Commit |
|----|----------|--------|------------------------|--------|
| P-001 | Low faithfulness on coding/operational outputs | deployed | BENCH-C-03 | 368bfb0 |
| P-002 | Extend fixer workflow to machine-enforceable checks | deployed | BENCH-C-01/02/04 | 90d9796 |
| P-003 | Fix validator prompts to reference actual outputs | deployed | BENCH-R-01 | 90d9796 |

---

## Exit Gate

Phase 3 is complete when all of the following are true:

- [x] Average executor/validator diff ≤ 1.0 across all 20 benchmarks. **0.69**
- [x] Agreement rate (within ±1.0) ≥ 70%. **75%**
- [x] Weakness miner produced at least 2 reports. **3 reports**
- [x] At least 3 harness improvement proposals filed in `proposals/`. **P-001, P-002, P-003**
- [x] At least 1 proposal implemented and re-validated by `tools/revalidate_benchmarks.py`. **3 deployed**
- [x] This file updated with final metrics.
- [ ] Human approves exit.
