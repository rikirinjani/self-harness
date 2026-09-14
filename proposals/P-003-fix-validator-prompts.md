# Harness Improvement Proposal: P-003

**Status:** draft  
**Weakness ID(s):** WM-2026-09-14-v2-004  
**Affected agent / workflow:** validator / benchmark prompts  
**Proposed by:** orchestrator  
**Date:** 2026-09-14  

---

## 1. Weakness Evidence

### Validator gap
- Benchmark(s): `BENCH-C-03` (resolved during P-001), `BENCH-R-01`
- Executor avg: `4.88`
- GPT validator avg: `1.00` (BENCH-R-01)
- Diff: `3.88`
- Quality axes most affected: `faithfulness`, `completeness`, `correctness`

### Observation
The validator prompt for `BENCH-C-03` originally contained the placeholder text:

> [No output file found — benchmark was executed directly in agent session]

This caused the validator to score the benchmark as 1 on every axis, even though an output file existed. A similar issue may affect `BENCH-R-01` and other early benchmarks.

### Trace records
- `traces/pm1-validator-verification.pm1`
- `traces/pm1-validator-retrace.pm1`

---

## 2. Proposed Change

Update the validator prompt generator so that prompts always reference the actual benchmark output file if one exists:

1. `validator/generate_prompts.py` should check `benchmarks/outputs/` for the latest output matching the benchmark ID.
2. If an output file exists, embed or reference it in the prompt.
3. If no output exists, keep the placeholder but add a clear instruction to the validator to distinguish "no output" from "output that does not meet criteria".

Target files:
- `validator/generate_prompts.py`
- `validator/prompts/*.txt` (regenerate)

---

## 3. Verification Plan

- Primary: `BENCH-R-01`
- Secondary: `BENCH-C-03` (already improved; confirm prompt remains correct)

Expected outcome after change:
- Validator scores for `BENCH-R-01` reflect the actual output quality, not a missing-file assumption.
- `tools/revalidate_benchmarks.py BENCH-R-01` shows reduced diff.

---

## 4. Risk and Rollback Plan

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Regenerated prompts overwrite manual edits | medium | medium | Version-control the prompts; review diff before commit. |
| Prompt becomes too long for some validators | low | low | Truncate or summarize long outputs. |

Rollback: revert `validator/generate_prompts.py` and restore previous prompt files.

---

## 5. Human Approval

- [ ] Human has reviewed this proposal.
- [ ] Human approves implementation.
- [ ] Human approves deployment after re-validation.

**Approver:** ___________________  
**Date:** ___________________  

---

## 6. Post-Implementation Notes

- Implementation commit: `{sha}`
- Re-validation result: `{pass / fail / partial}`
- Measured diff after change: `{X.XX}`
- Decision: `{deployed / rejected / needs iteration}`
