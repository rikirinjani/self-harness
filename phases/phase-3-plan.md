# Phase 3 Plan: Weakness-Driven Harness Improvement

**Status:** Draft — awaiting human ratification  
**Prerequisite:** Phase 2 complete + validator comparison report exists  
**Entry date target:** 2026-09-14  
**Duration estimate:** 2–3 weeks of focused sessions

---

## Goal

Close the gap between self-reported executor scores and independent GPT validator scores, then turn validated weaknesses into concrete harness improvements.

From the local validator run (2026-09-14):

| Metric | Value |
|--------|------:|
| Executor average | 4.91 |
| GPT validator average | 3.51 |
| Average diff | 1.40 |
| Agreement rate (±1.0) | 0% |
| Flagged benchmarks (diff > 1.5) | 8 |

Phase 3 is complete when the executor/validator gap is measurably reduced and at least one harness change has been implemented, verified, and recorded.

---

## Deliverables

### 1. Automated Weakness Miner

A script at `tools/weakness_miner.py` that reads:
- `benchmarks/results/summary.json`
- `validator/comparisons/comparison_report.md`
- `failures/*.json`
- `traces/*.pm1` (and future `.json` traces)

And produces:
- Clustered weakness themes (e.g., "verdict inflation on coding tasks", "missing edge-case tests", "encoding bugs on Windows").
- Frequency counts per agent type and per quality axis.
- A ranked list of harness improvement candidates.
- Output to `proposals/weakness-miner-report-YYYY-MM-DD.md`.

### 2. Harness Improvement Proposal Template

A reusable template at `proposals/TEMPLATE-harness-improvement.md` with sections for:
- Weakness evidence (validator diff, failure records, trace refs).
- Proposed change.
- Affected agent / workflow.
- Verification plan (which benchmark or test will detect the fix).
- Risk and rollback plan.
- Human approval signature.

### 3. Flagged-Benchmark Re-Run Pipeline

A script at `tools/revalidate_benchmarks.py` that:
- Accepts a list of benchmark IDs (defaults to currently flagged set).
- Re-runs each benchmark through the executor.
- Re-invokes the GPT validator prompts (or re-parses stored responses).
- Updates `validator/comparisons/comparison_report.md`.
- Exits non-zero if any benchmark still has diff > 1.5.

This lets us verify that a harness change actually reduces the gap.

### 4. Updated Phase Progress Tracking

Create and keep current:
- `phases/phase-3-progress.md`

With a table:

| Date | Flagged count | Avg diff | Agreement rate | Improvements proposed | Improvements merged |
|------|--------------:|---------:|---------------:|----------------------:|--------------------:|
| 2026-09-14 | 8 | 1.40 | 0% | 0 | 0 |

---

## Entry Criteria (must all pass before Phase 3 work begins)

- [x] Phase 2 gate met: 20/20 benchmarks executed, results recorded.
- [x] Validator comparison report exists at `validator/comparisons/comparison_report.md`.
- [x] At least 5 flagged benchmarks identified (actual: 8).
- [x] Local repo synced to GitHub on branch `sync-phase2`.
- [ ] Human ratifies this plan.

---

## Exit Criteria / Gate

Phase 3 is complete when **all** of the following are true:

- [ ] Average executor/validator diff ≤ 1.0 across all 20 benchmarks.
- [ ] Agreement rate (within ±1.0) ≥ 70%.
- [ ] Weakness miner produced at least 2 reports.
- [ ] At least 3 harness improvement proposals filed in `proposals/`.
- [ ] At least 1 proposal implemented and re-validated by the re-run pipeline.
- [ ] `phases/phase-3-progress.md` updated with final metrics.
- [ ] Human approves exit.

---

## Execution Strategy

### Week 1 — Mine and Propose

1. Run `tools/weakness_miner.py` to cluster weaknesses from the current comparison report and failure backlog.
2. File the top 3–5 clusters as formal proposals using `proposals/TEMPLATE-harness-improvement.md`.
3. Prioritize proposals by: (a) validator diff magnitude, (b) frequency in failure records, (c) feasibility.

### Week 2 — Implement and Re-validate

1. Pick the highest-priority proposal that has a clear benchmark-based verification plan.
2. Implement the harness change in a feature branch.
3. Run `tools/revalidate_benchmarks.py` against the affected benchmarks.
4. If the gap does not shrink, iterate or abandon the proposal and record the reason.

### Week 3 — Consolidate and Exit

1. Update `phases/phase-3-progress.md` with final numbers.
2. Merge validated changes to `sync-phase2` (and then to `main` via PR).
3. Write a Phase 3 exit memo in `phases/phase-3-progress.md`.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| GPT validator scores drift between runs | Fix the prompt template; run each benchmark 3× and take median. |
| Local backlog traces use `.pm1` not the planned `.json` schema | Accept `.pm1` as a legacy format for Phase 3; migrate to `.json` as a cleanup task. |
| Proposals are too vague to implement | Require each proposal to name the benchmark that will detect the fix. |
| Harness change breaks existing behavior | Use git worktrees; run `benchmarks/run.py --all` before and after. |
| Human approval bottleneck | Keep proposals small and incremental; one proposal per session when possible. |

---

## Resources

- Phase 2 results: `benchmarks/results/`
- Validator comparison: `validator/comparisons/comparison_report.md`
- Failure database: `failures/`
- Trace database: `traces/`
- Quality axes: `constitution.md` §Article II
- Benchmark definitions: `benchmark_catalog.md`
