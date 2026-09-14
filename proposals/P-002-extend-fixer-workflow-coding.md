# Harness Improvement Proposal: P-002

**Status:** draft  
**Weakness ID(s):** WM-2026-09-14-v2-001  
**Affected agent / workflow:** fixer / remaining coding benchmarks  
**Proposed by:** orchestrator  
**Date:** 2026-09-14  

---

## 1. Weakness Evidence

### Validator gap
- Benchmark(s): `BENCH-C-01`, `BENCH-C-02`, `BENCH-C-04`
- Executor avg: `4.96`
- GPT validator avg: `2.41`
- Diff: `2.55`
- Quality axes most affected: `correctness`, `actionability`, `faithfulness`

### Failure records
- `failures/2026-08-30-execution-fixer-silent-empty.json`
- `failures/2026-08-30-execution-fixer-silent-empty-2.json`
- Multiple coding-task failures where the fixer completed silently or skipped verification.

### Trace records
- `traces/fix-1-reconcile.pm1`
- `traces/20260819T211028-Fixer-cli.pm1`

---

## 2. Proposed Change

Extend P-001 by making the constraint restatement and self-check **machine-enforceable**:

1. Before editing, the fixer must write `constraints.md` next to the target file listing the spec constraints.
2. After editing, the fixer must run `tools/constraint_check.py --spec constraints.md --impl {target}`.
3. The orchestrator must refuse to mark the task complete unless `constraint_check.py` exits 0.

This raises the cost of skipping verification and makes the P-001 rule harder to ignore.

Target files:
- `rules/fixer-workflow.md` — add the machine-enforceable requirement.
- `tools/constraint_check.py` — already exists; may need refinement.

---

## 3. Verification Plan

- Primary: `BENCH-C-01` (Bounded Implementation)
- Secondary: `BENCH-C-02`, `BENCH-C-04`

Expected outcome after change:
- Average diff for BENCH-C-01/02/04 drops below `1.0`.
- `tools/revalidate_benchmarks.py BENCH-C-01 BENCH-C-02 BENCH-C-04` exits 0.

---

## 4. Risk and Rollback Plan

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| constraint_check.py gives false negatives | medium | low | Keep the parser simple; allow override with human approval. |
| Extra file clutter | low | low | Store constraints.md in a temp or trace-specific directory. |

Rollback: remove the machine-enforceable requirement from `rules/fixer-workflow.md`.

---

## 5. Human Approval

- [x] Human has reviewed this proposal.
- [x] Human approves implementation.
- [x] Human approves deployment after re-validation.

**Approver:** rikirinjani  
**Date:** 2026-09-14  

---

## 6. Post-Implementation Notes

- Implementation commit: `90d9796`
- Re-validation result: pass
- Measured diff after change: BENCH-C-01 0.25, BENCH-C-02 0.25, BENCH-C-04 0.13
- Decision: deployed
