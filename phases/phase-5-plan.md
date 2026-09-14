# Phase 5 Plan: Harness Architect / Controlled Evolution

**Status:** Active  
**Entry date:** 2026-09-14  
**Prerequisite:** Phase 4 complete  
**Duration estimate:** 2–3 weeks

---

## Goal

Move from human-implemented proposals to an automated **Harness Architect** that:
1. Reads approved proposals.
2. Generates concrete harness diffs (prompt/rule changes).
3. Applies them in an isolated **shadow harness**.
4. Re-runs benchmarks in shadow mode.
5. Reports whether the change improves the gap before human deployment.

---

## Deliverables

### 1. JSON proposal schema

Convert the markdown proposal template into a structured JSON schema so the architect can read and act on proposals programmatically.

Example file: `proposals/proposals.json` or per-proposal `.json` files.

### 2. Shadow harness

Create a `shadow/` directory that is a clean copy of the active harness rules (starting with `rules/`). The architect applies changes only inside `shadow/`.

### 3. `tools/harness_architect.py`

Reads an approved proposal and generates the corresponding harness diff:
- For workflow rules: produce a modified `.md` file in `shadow/rules/`.
- For validator prompts: produce a modified `validator/generate_prompts.py` snippet.
- For tool helpers: produce a new `shadow/tools/*.py`.

### 4. `tools/apply_harness_change.py`

Applies an architect-generated diff to `shadow/`, runs the benchmark suite, and compares shadow results against baseline.

### 5. Shadow benchmark runner

`benchmarks/run.py --shadow` uses `shadow/rules/` instead of `rules/` when executing benchmarks (where applicable).

### 6. Phase progress tracking

`phases/phase-5-progress.md` with baseline, candidate changes, shadow results, and exit gate.

---

## Entry Criteria

- [x] Phase 4 exit gate met.
- [x] ≥1 approved proposal exists (P-001, P-002, P-003, P-004).
- [x] Weakness miner and re-validation pipeline exist.

---

## Exit Criteria / Gate

Phase 5 is complete when:

- [ ] JSON proposal schema defined and at least 3 proposals converted.
- [ ] Shadow harness directory exists and is isolated from active harness.
- [ ] `tools/harness_architect.py` generates diffs from approved proposals.
- [ ] `tools/apply_harness_change.py` runs shadow benchmarks end-to-end.
- [ ] At least 1 approved proposal tested in shadow mode with a report.
- [ ] Human approves exit.

---

## Execution Strategy

### Week 1 — Schema and Shadow

1. Define JSON schema for proposals.
2. Convert P-001..P-004 to JSON.
3. Create `shadow/` directory and populate with copies of active rules.

### Week 2 — Architect and Apply

1. Build `tools/harness_architect.py`.
2. Build `tools/apply_harness_change.py`.
3. Wire shadow mode into `benchmarks/run.py`.

### Week 3 — Shadow Run and Report

1. Run shadow test for P-004 (orchestrator checklist).
2. Compare shadow results to baseline.
3. Write report and update progress.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Shadow diverges from active harness | Copy rules into `shadow/` at phase start; diff before/after. |
| Architect misinterprets proposal | Keep diff generation rule-based and auditable; human reviews shadow diff. |
| Shadow benchmarks not representative | Use same inputs/outputs as active benchmarks; only rules differ. |

---

## Resources

- Active proposals: `proposals/P-001..P-006.md`
- Active rules: `rules/`
- Validator: `validator/`
- Benchmark runner: `benchmarks/run.py`
