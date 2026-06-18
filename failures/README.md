# Failure Records

Structured failure records from subagent executions. Each failure is a JSON file named
`{timestamp}-{category}-{severity}-{task-slug}.json`.

## Schema

```json
{
  "failure_id": "uuid",
  "timestamp": "ISO8601",
  "trace_id": "parent-trace-uuid",
  "category": "tool|workflow|reasoning|config|communication",
  "severity": "critical|major|minor|cosmetic",
  "root_cause": "if known",
  "trace_summary": "compressed causal chain",
  "failure_signature": {
    "verifier_cause": "missing_artifact|timeout|assertion_failure",
    "agent_behavior": "explored_endlessly|deleted_required_file|wrong_api",
    "agent_mechanism": "no_early_output|no_recovery_after_error|wrong_tool_choice"
  }
}
```

## Status

Phase 1 — collection not yet active.
