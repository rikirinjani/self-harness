# Benchmark Catalog

**Version:** 1.0  
**Status:** Initial (slots defined, tasks to be specified)  
**Total benchmarks:** 20  
**Distribution:** 5 Research, 5 Coding, 5 Planning, 5 Operational  

---

## Benchmark ID Scheme

`BENCH-{CATEGORY}-{NN}`

| Prefix | Category | Responsible Agent(s) |
|--------|----------|---------------------|
| BENCH-R | Research | explorer, librarian |
| BENCH-C | Coding | fixer |
| BENCH-P | Planning | oracle, orchestrator |
| BENCH-O | Operational | fixer, orchestrator |

---

## Research Benchmarks (5)

### BENCH-R-01: Codebase Pattern Discovery
- **Description:** Given a codebase path and a pattern description, locate all relevant files and summarize their function.
- **Success criteria:** Returns complete file list with correct functional summaries. No false positives. No missed files.
- **Failure criteria:** Missing relevant files, incorrect summaries, hallucinated files.
- **Difficulty:** Medium
- **Responsible:** explorer

### BENCH-R-02: Library API Research
- **Description:** Given a library name and a specific use case, find the correct API, its parameters, and a working example from official docs.
- **Success criteria:** Returns correct API signature, parameters with types, and a verifiable example. Sources cited.
- **Failure criteria:** Wrong API version, hallucinated parameters, example doesn't compile.
- **Difficulty:** Medium
- **Responsible:** librarian

### BENCH-R-03: Comparative Analysis
- **Description:** Given a problem statement and 3 candidate approaches, produce a structured comparison with trade-offs, recommendations, and evidence.
- **Success criteria:** Each approach evaluated on ≥3 axes. Recommendation justified with evidence. Trade-offs explicit.
- **Failure criteria:** Missing approach, single-axis evaluation, recommendation without justification.
- **Difficulty:** High
- **Responsible:** oracle

### BENCH-R-04: Failure Pattern Analysis
- **Description:** Given a set of execution traces with known failures, cluster failures by root cause and produce structured weakness descriptions.
- **Success criteria:** Correct clustering by causal mechanism (not surface symptom). Each cluster has ≥2 supporting traces.
- **Failure criteria:** Clustering by symptom only, missed root cause, clusters with single trace.
- **Difficulty:** High
- **Responsible:** oracle, weakness-miner (future)

### BENCH-R-05: Documentation Accuracy Audit
- **Description:** Given a documentation file and the source code it describes, find all inaccuracies, omissions, and stale references.
- **Success criteria:** Every inaccuracy documented with line reference to both doc and source. Severity rated.
- **Failure criteria:** Misses clear inaccuracy, flags correct content, no severity rating.
- **Difficulty:** Medium
- **Responsible:** explorer, oracle

---

## Coding Benchmarks (5)

### BENCH-C-01: Bounded Implementation
- **Description:** Given a spec with inputs, outputs, and constraints, implement a single-function solution. Must compile and pass provided tests.
- **Success criteria:** Code compiles. All provided tests pass. No new dependencies. Follows project style.
- **Failure criteria:** Doesn't compile, tests fail, ignores constraints, introduces unnecessary abstraction.
- **Difficulty:** Low
- **Responsible:** fixer

### BENCH-C-02: Bug Fix with Regression Check
- **Description:** Given a failing test and source code, fix the bug such that the failing test passes AND all existing tests still pass.
- **Success criteria:** Bug test passes. All other tests pass. Fix is minimal (changes only what's needed).
- **Failure criteria:** Breaks existing tests. Overly broad fix. Fix introduces new bug.
- **Difficulty:** Medium
- **Responsible:** fixer

### BENCH-C-03: Refactor for Clarity
- **Description:** Given working but unreadable code, refactor for clarity without changing behavior. Test suite must still pass.
- **Success criteria:** Test suite passes. Code is more readable (shorter, clearer names, better structure). Behavior preserved.
- **Failure criteria:** Changes behavior. Test suite fails. Makes code longer without improving clarity. Introduces bugs.
- **Difficulty:** Medium
- **Responsible:** fixer, oracle (review)

### BENCH-C-04: Multi-File Feature Addition
- **Description:** Given a project with established patterns, add a feature that touches 3+ files following existing conventions.
- **Success criteria:** Feature works. Follows existing patterns. Tests pass. No unrelated changes.
- **Failure criteria:** Breaks existing functionality. Ignores project conventions. Missing tests. Changes unrelated files.
- **Difficulty:** High
- **Responsible:** fixer

### BENCH-C-05: Scripting / Automation
- **Description:** Given an operational need (file processing, data transform, report generation), write a shell script or utility.
- **Success criteria:** Script runs without error. Produces correct output. Handles edge cases (empty input, missing files). Includes usage help.
- **Failure criteria:** Runtime error on happy path. No error handling. Unclear usage. Produces wrong output.
- **Difficulty:** Low
- **Responsible:** fixer

---

## Planning Benchmarks (5)

### BENCH-P-01: Task Decomposition
- **Description:** Given a high-level goal, decompose into a dependency-ordered task list with estimated effort per task.
- **Success criteria:** Tasks are independent where possible. Dependencies explicit. Estimates have confidence ranges. No missing critical path.
- **Failure criteria:** Missing dependency. Overly coarse decomposition. No effort estimates. Circular dependency.
- **Difficulty:** Medium
- **Responsible:** oracle

### BENCH-P-02: Risk Assessment
- **Description:** Given a plan or proposal, identify top 5 risks with likelihood, impact, and mitigation for each.
- **Success criteria:** Risks are specific (not generic). Likelihood and impact are scored. Mitigation is concrete. Second-order risks identified.
- **Failure criteria:** Generic risks ("things might go wrong"). Missing mitigation. Unscored risks. Obvious risk missed.
- **Difficulty:** Medium
- **Responsible:** oracle

### BENCH-P-03: Architecture Decision
- **Description:** Given a technical decision with trade-offs, produce a structured ADR with context, options, decision, and consequences.
- **Success criteria:** All options evaluated on same criteria. Decision rationale explicit. Consequences include positives AND negatives.
- **Failure criteria:** Missing options. Biased evaluation. No consequences. Decision not tied to requirements.
- **Difficulty:** High
- **Responsible:** oracle

### BENCH-P-04: Resource-Constrained Planning
- **Description:** Given a goal and hard constraints (time, budget, team), produce a plan that respects all constraints.
- **Success criteria:** Plan fits within constraints. Trade-offs are explicit. If constraints make goal impossible, says so clearly.
- **Failure criteria:** Plan exceeds constraints without flagging it. Trade-offs hidden. Impossibility not identified.
- **Difficulty:** High
- **Responsible:** oracle

### BENCH-P-05: Retrospective / Root Cause Analysis
- **Description:** Given a failure event with timeline, produce a root cause analysis with contributing factors and prevention recommendations.
- **Success criteria:** Root cause is correct (not just proximate cause). Contributing factors identified. Recommendations are specific and actionable.
- **Failure criteria:** Confuses symptom with cause. Missing contributing factors. Vague recommendations.
- **Difficulty:** Medium
- **Responsible:** oracle, orchestrator

---

## Operational Benchmarks (5)

### BENCH-O-01: State Reporting
- **Description:** Given a directory or system state, produce a concise structured report of key metrics.
- **Success criteria:** Report is accurate. Format is consistent. All relevant metrics included. No irrelevant data.
- **Failure criteria:** Inaccurate numbers. Missing key metric. Excessive irrelevant detail. Unstructured output.
- **Difficulty:** Low
- **Responsible:** fixer, orchestrator

### BENCH-O-02: Diagnostic Execution
- **Description:** Given a symptom (error, failure, anomaly), run diagnostics, collect evidence, and produce a structured finding.
- **Success criteria:** Correct diagnostic commands chosen. Evidence collected before conclusion. Finding is specific.
- **Failure criteria:** Jumps to conclusion. Wrong diagnostic. Missing evidence. No finding.
- **Difficulty:** Medium
- **Responsible:** fixer

### BENCH-O-03: Configuration Change
- **Description:** Given a config file and required change, implement change safely with validation and rollback plan.
- **Success criteria:** Change applied correctly. Validation confirms it works. Rollback procedure documented.
- **Failure criteria:** Change breaks config. No validation. No rollback plan. Unrelated side effects.
- **Difficulty:** Medium
- **Responsible:** fixer

### BENCH-O-04: Bulk File Operation
- **Description:** Given a set of files and transformation rule, apply transformation with dry-run, confirmation, and verification.
- **Success criteria:** Dry-run shows correct changes. Actual run produces expected output. Verification confirms correctness.
- **Failure criteria:** Wrong files affected. No dry-run. No verification. Destructive without confirmation.
- **Difficulty:** Low
- **Responsible:** fixer

### BENCH-O-05: Workflow Automation
- **Description:** Given a multi-step manual process, produce an automated script that handles the full workflow with error handling.
- **Success criteria:** Script runs end-to-end. Each step checks prior step succeeded. Error messages are informative. Cleanup on failure.
- **Failure criteria:** Missing error handling. Steps not validated before proceeding. No cleanup. Script is fragile (hardcoded paths).
- **Difficulty:** High
- **Responsible:** fixer, oracle
