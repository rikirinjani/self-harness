# Fixer Workflow Rule — P-001

**Version:** 1.0  
**Status:** Approved for implementation  
**Applies to:** All fixer tasks (coding, scripting, operational code changes)  
**Owner:** self-harness program  

---

## Purpose

Increase the faithfulness score of fixer outputs by forcing explicit constraint restatement and a self-check before the task is considered complete.

---

## Workflow

For every fixer task, the orchestrator (or the fixer itself, if self-prompted) must perform these three steps:

### Step 1 — Restate constraints

Before writing or editing code, produce a short bullet list of the explicit constraints from the task spec:

- Inputs and expected outputs
- Forbidden operations or dependencies
- Style / format requirements
- Edge cases that must be handled
- Regression requirements (existing tests must still pass)

The list must be included in the trace output.

### Step 2 — Implement

Implement the change. Keep the constraint list visible while editing.

### Step 3 — Self-check against constraints

After implementation, verify each restated constraint:

- [ ] Code compiles / runs without errors.
- [ ] Provided tests pass.
- [ ] Existing tests still pass (regression check).
- [ ] No new dependencies were added unless explicitly allowed.
- [ ] Edge cases listed in Step 1 are handled.
- [ ] Output format matches the spec.

If any checkbox cannot be checked, the fixer must explain why in the trace and mark the task outcome accordingly (partial / fail).

---

## Tooling

A helper script exists at `tools/constraint_check.py`. It must be invoked by the orchestrator before the task is marked complete.

Usage:

```bash
python tools/constraint_check.py --spec constraints.md --impl "path/to/code.py"
```

The script returns a JSON object with:
- `constraints`: extracted constraint keywords
- `covered`: constraints found in the implementation
- `missing`: constraints not found
- `pass`: true if all constraints are covered

### Machine-enforceable requirement

1. The constraint restatement from Step 1 must be written to `constraints.md` in the task working directory.
2. After implementation, the orchestrator must run `tools/constraint_check.py --spec constraints.md --impl {target_file}`.
3. The task outcome must be marked `fail` or `partial` if the helper reports any missing constraints, unless the human explicitly overrides.
4. The `constraints.md` and the helper output must be attached to the trace.

---

## Trace requirement

Every fixer trace must contain:
1. The constraint restatement from Step 1.
2. The `constraints.md` file path.
3. The `tools/constraint_check.py` output.
4. The self-check results from Step 3.
5. A reference to this rule file (`rules/fixer-workflow.md`).

Failure to include these is itself a process failure.

---

## Rollback

If this rule causes unacceptable slowdown or does not reduce the executor/validator gap, revert to the previous workflow by removing the constraint restatement and self-check requirements from this file and committing the revert.
