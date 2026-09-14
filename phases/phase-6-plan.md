# Phase 6 Plan: Controlled Evolution

**Status:** Active  
**Entry date:** 2026-09-14  
**Prerequisite:** Phase 5 complete  
**Duration estimate:** 2–3 weeks

---

## Goal

Automate the promotion of shadow-approved harness changes into the active harness while preserving human veto and instant rollback.

The system must:
1. Read a shadow report that recommends `deploy`.
2. Wait for a human approval window (veto window).
3. If no veto, copy the shadow rule/tool into the active harness.
4. Re-run the validator to confirm the active harness improved or held steady.
5. If anything breaks, automatically roll back using the pre-change snapshot.

---

## Deliverables

### 1. Promotion gate

`tools/promote_shadow_change.py`:
- Reads a shadow report JSON.
- Checks recommendation == `deploy`.
- Writes a human approval request to `shadow/reports/P-NNN-awaiting-approval.json`.
- Upon explicit `--approve` flag (human action), copies shadow files to active locations.
- Refuses to promote if recommendation is `manual_review` or `rejected`.

### 2. Rollback system

`tools/rollback_harness_change.py`:
- Creates a pre-promotion snapshot of active rules under `shadow/snapshots/`.
- On failure, restores active files from snapshot.
- Verifies restoration by running `benchmarks/run.py --summary`.

### 3. Veto window log

`shadow/CHANGELOG.md`:
- Records every promotion attempt, approval decision, and rollback.

### 4. Update apply tool

`tools/apply_harness_change.py`:
- After shadow run, if recommendation == `deploy`, prints the promotion command and the veto window duration.

### 5. Phase progress tracking

`phases/phase-6-progress.md`.

---

## Entry Criteria

- [x] Phase 5 exit gate met.
- [x] Shadow harness and architect exist.
- [x] At least 1 shadow report recommends a change.

---

## Exit Criteria / Gate

Phase 6 is complete when:

- [x] Promotion tool copies shadow files to active harness on explicit approval.
- [x] Rollback tool restores active files from snapshot.
- [x] Veto/approval log exists.
- [x] At least 1 shadow-approved change promoted to active harness and re-validated.
- [x] Human approves exit.

---

## Execution Strategy

### Week 1 — Snapshot and Promotion

1. Build snapshot mechanism.
2. Build `tools/promote_shadow_change.py`.
3. Build `tools/rollback_harness_change.py`.

### Week 2 — Veto and Logging

1. Add approval request and `--approve` flag.
2. Add `shadow/CHANGELOG.md` updates.
3. Wire automatic promotion gate into `apply_harness_change.py`.

### Week 3 — End-to-End Run

1. Run controlled evolution on P-004.
2. Approve promotion.
3. Verify active harness includes the change and re-validate.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Auto-promotion bypasses human | Require `--approve` flag; default is veto/await state. |
| Rollback fails | Snapshot is a file copy; test rollback on every promotion. |
| Shadow report false positive | Only promote when recommendation == `deploy` and human approves. |

---

## Resources

- Shadow reports: `shadow/reports/`
- Active rules: `rules/`
- Snapshot storage: `shadow/snapshots/`
- Promotion tool: `tools/promote_shadow_change.py`
- Rollback tool: `tools/rollback_harness_change.py`
