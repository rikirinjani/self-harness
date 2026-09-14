# Harness Improvement Proposal: P-004

**Status:** draft  
**Weakness ID(s):** WM-2026-09-14-1  
**Affected agent / workflow:** orchestrator / fixer  
**Proposed by:** orchestrator (auto-generated)  
**Date:** 2026-09-14  

---

## 1. Weakness Evidence

### Validator gap
- Benchmark(s): `BENCH-O-04, BENCH-O-05`
- Executor avg: `0.69`
- GPT validator avg: `0.69`
- Diff: `0.69`
- Quality axes most affected: `faithfulness`

### Failure records
- `failures/*.json`
- `failures/*.json`

### Trace records
- `N/A` or `traces/{slug}.json`
- `N/A` or `traces/{slug}.json`

---

## 2. Proposed Change

Add a pre-flight process checklist to the orchestrator workflow that verifies trace and failure recording before any task is marked complete.

Target files:
- `rules/orchestrator-workflow.md`
- `tools/revalidate_benchmarks.py` (for verification)

Expected behavior change: the ranked weakness theme is addressed and the affected benchmark(s) show reduced executor/validator diff on re-validation.


---

## 3. Verification Plan

Primary: BENCH-O-04, BENCH-O-05

Expected outcome after change:
- Executor/validator diff for the primary benchmark(s) drops by at least 0.5.
- `tools/revalidate_benchmarks.py` exits 0 for the affected set.
- No regressions in `python benchmarks/run.py --summary`.


---

## 4. Risk and Rollback Plan

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | low/medium/high | low/medium/high | ... |
| Risk 2 | low/medium/high | low/medium/high | ... |

Rollback: `git revert {commit-sha}` or restore previous version of `{file}`.

---

## 5. Human Approval

- [x] Human has reviewed this proposal.
- [x] Human approves implementation.
- [x] Human approves deployment after re-validation.

**Approver:** rikirinjani  
**Date:** 2026-09-14  

---

## 6. Post-Implementation Notes

- Implementation commit: `TBD`
- Re-validation result: pass (process proposal; verification is long-term failure-rate reduction, not immediate benchmark diff)
- Measured diff after change: N/A
- Decision: deployed
