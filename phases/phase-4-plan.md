# Phase 4 Plan: Weakness Miner — Production

**Status:** Active  
**Entry date:** 2026-09-14  
**Prerequisite:** Phase 3 complete  
**Duration estimate:** 2–3 weeks

---

## Goal

Transform the Phase 3 ad-hoc weakness miner into a continuous, automated system that discovers harness weaknesses from multiple evidence sources and generates actionable improvement proposals.

---

## Deliverables

### 1. Multi-source weakness miner

Upgrade `tools/weakness_miner.py` to consume:
- `benchmarks/results/summary.json`
- `validator/comparisons/comparison_report.md`
- `failures/*.json`
- `traces/*.pm1` and `traces/*.json`

And produce:
- Benchmark-diff themes
- Failure-category trends
- Trace-pattern clusters
- Cross-source correlations (e.g., a benchmark weakness that also appears in failures)

### 2. Automated proposal generator

Create `tools/propose_harness_change.py` that:
- Reads the latest weakness miner report.
- Selects the highest-priority theme.
- Generates a `proposals/P-NNN-*.md` file from `proposals/TEMPLATE-harness-improvement.md`.
- Fills in evidence, benchmark verification, and risk sections automatically.

### 3. Scheduled runner

Create `tools/daily_weakness_check.py` that:
- Runs the weakness miner.
- Compares current results to the previous run (if any).
- Generates new proposals only when a new high-priority theme appears or a known theme worsens.
- Updates `ops/dashboard.md` with trend data.

### 4. Operational dashboard

Create/update `ops/dashboard.md` with:
- Weekly weakness counts
- Top failure categories
- Benchmarks with increasing diff
- Recently auto-filed proposals

### 5. Phase progress tracking

Create `phases/phase-4-progress.md` with:
- Baseline metrics
- Cumulative auto-proposal count
- Deployed auto-proposals
- Exit gate checklist

---

## Entry Criteria

- [x] Phase 3 exit gate met.
- [x] `tools/weakness_miner.py` exists.
- [x] Failure and trace databases exist.
- [x] Validator comparison report exists.

---

## Exit Criteria / Gate

Phase 4 is complete when all of the following are true:

- [ ] Weakness miner integrates at least 3 evidence sources.
- [ ] At least 3 harness improvement proposals generated automatically.
- [ ] At least 1 auto-generated proposal reviewed, approved, and deployed through Phase 3 pipeline.
- [ ] `tools/daily_weakness_check.py` runs end-to-end.
- [ ] `ops/dashboard.md` shows weakness trends over time.
- [ ] `phases/phase-4-progress.md` updated with final metrics.
- [ ] Human approves exit.

---

## Execution Strategy

### Week 1 — Integrate and Mine

1. Upgrade `tools/weakness_miner.py` to parse traces and failures.
2. Add cross-source correlation logic.
3. Produce a consolidated report.

### Week 2 — Automate Proposals

1. Build `tools/propose_harness_change.py`.
2. Generate the first 3 auto-proposals.
3. Have the human review and approve at least one.

### Week 3 — Schedule and Dashboard

1. Build `tools/daily_weakness_check.py`.
2. Create `ops/dashboard.md`.
3. Run the daily check and verify it updates the dashboard.
4. Deploy the approved auto-proposal and re-validate.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Auto-proposals are low quality | Require human review before deployment; template includes evidence sections. |
| Weakness themes drift between runs | Store previous miner output and diff against it. |
| Trace `.pm1` format is hard to parse | Accept both `.pm1` JSON records and plain text; migrate to `.json` as cleanup. |
| Too many auto-proposals | Daily runner only generates proposals for new or worsening themes. |

---

## Resources

- Phase 3 assets: `tools/weakness_miner.py`, `validator/comparisons/comparison_report.md`
- Failure database: `failures/`
- Trace database: `traces/`
- Proposal template: `proposals/TEMPLATE-harness-improvement.md`
