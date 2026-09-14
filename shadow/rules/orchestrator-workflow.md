# Orchestrator Workflow Rule — P-004

**Version:** 1.0
**Status:** Approved for implementation
**Applies to:** All orchestrator task sessions
**Owner:** self-harness program

---

## Purpose

Reduce recurring process-category failures by enforcing a pre-flight and post-flight checklist on every orchestrator-led task.

---

## Pre-flight checklist

Before starting work, the orchestrator must confirm:

- [ ] `STATE.md` has been read (Loop Mode rule).
- [ ] A `task_id` is assigned to the session.
- [ ] The appropriate agent lane has been selected (explorer, fixer, designer, oracle, etc.).
- [ ] The scope of the task is documented in the trace payload.

## Post-flight checklist

Before marking a task complete, the orchestrator must confirm:

- [ ] A PM-1 trace has been written to `traces/` with `--key-files` for every touched file.
- [ ] If the task failed or partially failed, a failure record has been written to `failures/` with `category`, `severity`, `root_cause`, and `failure_signature`.
- [ ] `STATE.md` has been updated if this was a loop run.
- [ ] `tools/retrace.py` would report the project as trace-clean for the files touched.

## Trace requirement

Every orchestrator trace must reference this rule file (`rules/orchestrator-workflow.md`) in its `action` or payload.

## Rollback

If this rule causes unacceptable overhead, reduce the checklist to the two highest-impact items (trace + failure recording) and commit the simplified version.


### P-004 (shadow addition)

Add a pre-flight and post-flight process checklist to the orchestrator workflow. Enforce trace and failure recording before any task is marked complete.
