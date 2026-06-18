# Execution Traces

Trace records for subagent task executions. Each trace is a JSON file named
`{timestamp}-{agent}-{task-slug}.json`.

## Schema

```json
{
  "trace_id": "uuid",
  "timestamp": "ISO8601",
  "agent": "fixer|explorer|designer|librarian|oracle|observer",
  "task_description": "...",
  "subagent_type": "...",
  "execution_trace": ["step1", "step2", ...],
  "outcome": "pass|fail",
  "duration_ms": 12345,
  "tool_calls": 7,
  "harness_version": "v1.0"
}
```

## Status

Phase 1 — collection not yet active.
