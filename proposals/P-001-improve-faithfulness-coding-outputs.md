# Harness Improvement Proposal: P-001

**Status:** draft  
**Weakness ID(s):** WM-2026-09-14-003  
**Affected agent / workflow:** fixer / coding task execution  
**Proposed by:** orchestrator  
**Date:** 2026-09-14  

---

## 1. Weakness Evidence

### Validator gap
- Benchmark(s): `BENCH-C-01`, `BENCH-C-02`, `BENCH-C-03`, `BENCH-C-04`, `BENCH-O-04`, `BENCH-O-05`, `BENCH-P-04`, `BENCH-R-01`
- Executor avg: `4.91`
- GPT validator avg: `3.51`
- Diff: `1.40`
- Quality axes most affected: `faithfulness`, `correctness`, `actionability`

### Failure records
- `failures/2026-09-14-command-loop-task006-freeze.json`
- `failures/2026-09-11-interface-contract-pm1rx-lane-g-codec-jsondecode.json`
- Multiple `process` and `tool` category failures in the backlog that trace back to outputs not following constraints precisely.

### Trace records
- `traces/fix-1-reconcile.pm1`
- `traces/pm1-validator-verification.pm1`
- Coding and operational traces where the agent passed self-checks but external validation found deviations.

---

## 2. Proposed Change

Introduce a **constraint-restating + diff-against-spec** step in the fixer workflow for all coding and operational tasks:

1. Before writing code, the fixer must restate the explicit constraints from the task spec in a short bullet list.
2. After implementing, the fixer must run a self-check that verifies the output matches each restated constraint.
3. The restatement and self-check must be included in the trace output.

Target files:
- `rules/fixer-workflow.md` — project-level fixer workflow instruction (approved by human).
- `tools/constraint_check.py` — lightweight harness guard that parses a spec snippet and reports missing constraints.

Expected behavior change: executor scores on `faithfulness` and `actionability` should move closer to validator scores because the agent is forced to demonstrate that it followed constraints rather than assuming it did.

---

## 3. Verification Plan

Which benchmark(s) will detect whether this change works?

- Primary: `BENCH-C-03` (Refactor for Clarity — currently validator avg 1.00, the worst gap)
- Secondary: `BENCH-C-01`, `BENCH-C-02`

Expected outcome after change:
- Executor/validator diff for `BENCH-C-03` drops from `4.00` to `<= 1.5` (ideally `<= 1.0`).
- No regressions in `python benchmarks/run.py --summary`.
- `tools/revalidate_benchmarks.py BENCH-C-03` exits successfully (diff <= 1.5).

---

## 4. Risk and Rollback Plan

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Extra step slows fixer tasks | medium | low | Keep restatement to 3–5 bullets; do not require prose essays. |
| Constraint restatement becomes boilerplate | medium | low | Review a sample of traces; refine prompt if restatements are generic. |
| Change does not reduce validator gap | high | medium | If re-validation shows no improvement, abandon the prompt change and try a different intervention. |

Rollback: `git revert {commit-sha}` or restore previous version of the affected agent instruction file.

---

## 5. Human Approval

- [x] Human has reviewed this proposal.
- [x] Human approves implementation.
- [ ] Human approves deployment after re-validation.

**Implementation artifacts:**
- `rules/fixer-workflow.md`
- `tools/constraint_check.py`

**Approver:** rikirinjani  
**Date:** 2026-09-14  

---

## 6. Post-Implementation Notes

Fill in after the change has been implemented and re-validated.

- Implementation commit: `{sha}`
- Re-validation result: `{pass / fail / partial}`
- Measured diff after change: `{X.XX}`
- Decision: `{deployed / rejected / needs iteration}`
