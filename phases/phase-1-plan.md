# Phase 1 Plan: Observation Infrastructure

**Prerequisite:** Phase 0 complete (governance in place, repo pushed)  
**Entry target:** 50 logged tasks, 10+ failures, 3+ failure categories  
**Duration estimate:** ~2 weeks of normal usage

---

## What Phase 1 Builds

A structured trace and failure database that feeds the Weakness Miner (Phase 4).
The system records what agents do, what fails, and why — so later phases can mine
patterns and propose harness improvements.

## Deliverables

### 1. Trace Collection Schema

File: `traces/{timestamp}-{agent}-{slug}.json`

```json
{
  "trace_id": "uuid",
  "timestamp": "2026-06-18T12:00:00Z",
  "agent": "fixer",
  "task_description": "Benchmark BENCH-C-02: fix bug with regression check",
  "subagent_type": "fixer",
  "execution_trace": [
    "read source file",
    "identify root cause",
    "edit src/buggy.ts:42",
    "run pytest",
    "all tests pass"
  ],
  "outcome": "pass",
  "duration_ms": 45200,
  "tool_calls": 12,
  "harness_version": "v1.0"
}
```

Every subagent task I dispatch gets a trace record. Pass or fail, it gets logged.

### 2. Failure Logging Schema

File: `failures/{timestamp}-{severity}-{category}-{slug}.json`

```json
{
  "failure_id": "uuid",
  "timestamp": "2026-06-18T12:00:00Z",
  "trace_id": "parent-trace-uuid",
  "category": "workflow",
  "severity": "major",
  "root_cause": "fixer did not verify existing tests still pass after edit",
  "trace_summary": "Edited file, ran only the new test (passed), but broke existing test in same suite",
  "failure_signature": {
    "verifier_cause": "existing_test_failed",
    "agent_behavior": "only_ran_new_test",
    "agent_mechanism": "no_regression_check_in_workflow"
  }
}
```

The `failure_signature` field is critical — it's what the Weakness Miner uses to
cluster failures by causal mechanism, not surface symptom (per the Self-Harness paper).

### 3. Task Distribution Requirement

The spec requires diversity across 5 task types:

| Type | Count | Examples |
|------|-------|----------|
| Research | 10 | Codebase search, API research, comparative analysis |
| Coding | 10 | Implementation, bug fix, refactor, automation |
| Planning | 10 | Task decomposition, risk assessment, ADR |
| Operational | 10 | State reporting, diagnostics, config changes |
| Mixed | 10 | Multi-step workflows combining above |

### 4. Failure Diversity Requirement

At least 3 of these categories represented:

| Category | Example |
|----------|---------|
| Tool failures | Agent calls wrong tool, tool errors, tool timeout |
| Workflow failures | Skipped verification, wrong order, missing step |
| Reasoning failures | Wrong conclusion, hallucinated API, circular logic |
| Configuration failures | Wrong settings, missing config, bad params |
| Communication failures | Unclear output, wrong audience, missing context |

---

## How to Execute Phase 1

### Step 1 — Instrument the Orchestrator

After every subagent dispatch + completion, I automatically log a trace record.
For failures, I also write a failure record with the `failure_signature`.

Concretely, this means at the end of a subagent task I:

```
1. Assess outcome (pass/fail)
2. If fail → classify (category, severity, root cause, failure signature)
3. Write JSON file to ~/self-harness/traces/ or ~/self-harness/failures/
4. Git commit and push after each batch
```

### Step 2 — Work Through Normal Tasks

No special test harness needed yet. Every task I do for existing projects
(ai-trader-agent, farmawatch, open-design, etc.) generates trace data.
The diversity requirement just means I should consciously vary what I ask
agents to do — not only coding, but also research, planning, and ops.

### Step 3 — Track Progress

| Metric | Target | Current |
|--------|--------|---------|
| Total tasks logged | 50 | 0 |
| Total failures | 10+ | 0 |
| Failure categories | 3+ | 0 |
| Task type diversity | 5 types | 0 |

Update this table in `phases/phase-1-progress.md` as data accumulates.

### Step 4 — Phase-Out Gate

Phase 1 is complete when:

- [ ] ≥50 trace records in `traces/`
- [ ] ≥10 failure records in `failures/`
- [ ] ≥3 failure categories represented
- [ ] All 5 task types represented (≥10 each)
- [ ] All logs use the structured schema above

When these pass → proceed to Phase 2.

---

## Automation Ideas (Future)

Once Phase 1 proves the schema works, I could build a simple shell script or
OpenCode command that semi-automates trace logging:

```bash
# ~/.config/opencode/commands/log-trace.md
# Usage: /log-trace agent="fixer" outcome="fail" category="workflow"
```

But for now, manual logging during normal work is fine. The key is **consistency**:
every subagent task gets logged, not just the interesting failures.
