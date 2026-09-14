# Harness Improvement Proposal: {PROPOSAL_ID}

**Status:** draft  
**Weakness ID(s):** {W-XXX or benchmark refs}  
**Affected agent / workflow:** {orchestrator / fixer / designer / explorer / etc.}  
**Proposed by:** {agent or human}  
**Date:** {YYYY-MM-DD}  

---

## 1. Weakness Evidence

### Validator gap
- Benchmark(s): `{BENCH-X-NN}`
- Executor avg: `{X.XX}`
- GPT validator avg: `{X.XX}`
- Diff: `{X.XX}`
- Quality axes most affected: `{correctness, completeness, ...}`

### Failure records
- `failures/{timestamp}-{category}-{slug}.json`
- `failures/{timestamp}-{category}-{slug}.json`

### Trace records
- `traces/{slug}.pm1` or `traces/{slug}.json`
- `traces/{slug}.pm1` or `traces/{slug}.json`

---

## 2. Proposed Change

Describe the harness change in one paragraph. Include file paths and expected behavior changes.

Example:
> Add a mandatory regression-test step to the fixer workflow so that every code edit runs the full existing test suite, not just the new test.

---

## 3. Verification Plan

Which benchmark(s) will detect whether this change works?

- Primary: `{BENCH-X-NN}`
- Secondary: `{BENCH-X-NN}`

Expected outcome after change:
- Executor/validator diff for primary benchmark drops from `{X.XX}` to `<= 1.0`.
- No regressions in `benchmarks/run.py --summary`.

---

## 4. Risk and Rollback Plan

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | low/medium/high | low/medium/high | ... |
| Risk 2 | low/medium/high | low/medium/high | ... |

Rollback: `git revert {commit-sha}` or restore previous version of `{file}`.

---

## 5. Human Approval

- [ ] Human has reviewed this proposal.
- [ ] Human approves implementation.
- [ ] Human approves deployment after re-validation.

**Approver:** ___________________  
**Date:** ___________________  

---

## 6. Post-Implementation Notes

Fill in after the change has been implemented and re-validated.

- Implementation commit: `{sha}`
- Re-validation result: `{pass / fail / partial}`
- Measured diff after change: `{X.XX}`
- Decision: `{deployed / rejected / needs iteration}`
