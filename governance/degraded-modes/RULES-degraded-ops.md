## Rule 11: Required review and degraded operation

This section governs review, dependency failures, recovery, and exceptions. It supplements Rules 1–10 without renumbering them. Where instructions conflict, this section controls review and degraded-operation handling; unrelated obligations remain in force. It does not itself grant write, push, or merge permission.

**Acceptance** means declaring a task complete, closing it, integrating its changes, or merging it. Producing a candidate or checkpoint is not acceptance. A blocked task must remain visibly blocked in `STATE.md`; do not mark its crash log complete.

### 11.1 Deterministic risk classification

Before implementation, classify the planned change. Reclassify against the actual diff before review. Apply the **union** of every matching row, including transitive effects. File names alone do not determine risk. Uncertain scope receives the stricter plausible classification until an independent reviewer or human resolves it with recorded reasons.

**Baseline gates for every L2+ change:**
- Explicit human L2 enablement, permitted role, git worktree, protected-resource restrictions, and attempt limits.
- Project-documented tests with retained raw results. Missing or unrunnable tests are a blocked gate, not a pass.
- Independent verifier dispatch after implementation and approval of the exact candidate revision.
- Required traces, quality records, archival, and file reconciliation under Rules 1–10.

| Deterministic trigger | Required gates in addition to the baseline |
|---|---|
| Source changes: executable code, scripts, templates, build inputs, generated executable artifacts, or runtime configuration | Run documented build, lint, and test commands where defined; add or update behavior/regression tests for changed behavior. Review the complete actual diff, including generated changes. |
| Dependency changes: manifest, lockfile, version, source, registry, vendored code, or dependency-resolution configuration | Retain resolved versions and provenance; perform a clean locked install/build, applicable compatibility tests, and dependency security/license checks. Unresolved findings block acceptance pending remediation or a permitted exception. |
| Authentication, authorization, secrets handling, persistence, migrations, transaction semantics, asynchronous execution, locking, or concurrency behavior | Mandatory Oracle escalation and domain-competent independent review. Exercise applicable negative authorization cases, data integrity and recovery/rollback, and race/failure paths. Record why any listed sub-gate is inapplicable; reviewer must confirm. Protected-file prohibitions still apply. |
| Public interfaces: externally consumed APIs, CLI behavior, events, schemas, serialization, configuration contracts, or documented compatibility promises | Mandatory Oracle escalation; contract and compatibility tests; explicit breaking-change assessment. A breaking change requires human approval of its migration/rollout plan before acceptance. |
| Governance/tooling: rules, roles, prompts controlling permissions, approval logic, evidence writers, scanners, validators, CI gates, orchestration, or agent tool access | Mandatory Oracle escalation; independent control review and regression tests for relevant denial, bypass, unavailable-dependency, and interrupted-session paths. Evaluate under the pre-change policy and trusted gate implementation; a candidate cannot authorize or validate its own weakened controls. |
| Any L2+ change not matched above, including documentation-only changes | Baseline gates remain mandatory. Run applicable structural/documentation validators. Low cost or small size does not remove verifier review. |

Anyone may escalate risk or request additional review. The implementer and orchestrator may not unilaterally downgrade classification, remove a triggered gate, or label a failed gate “not applicable.” Record classification, matched triggers, gates, and any independently confirmed correction in `STATE.md`.

### 11.2 Required-review contract

The implementer produces a committed candidate and identifies its repository, task ID, base commit, and candidate commit. Uncommitted task changes block review completion.

The reviewer must be a separately dispatched agent or an authorized human who did not implement the candidate. A new turn, persona, or self-review by the implementer does not qualify.

The reviewer must:

1. Obtain the requirements and acceptance criteria from their authoritative location.
2. Obtain read-only access to the exact base-to-candidate diff and candidate tree, including additions, deletions, renames, relevant generated artifacts, and dependency changes. Record a SHA-256 digest of the diff bytes actually inspected.
3. Independently obtain raw evidence from trusted storage or execute checks in an isolated environment. An implementer summary, pasted success message, or supplied evidence reference alone is not independent evidence.
4. Verify that evidence belongs to the same repository and exact candidate commit. Retain exact commands, exit codes, environment/tool versions, seeds where applicable, and raw output references with content hashes.
5. Evaluate every required gate. Missing, inaccessible, stale, conflicting, or incomplete evidence yields `REJECT`, not conditional approval.

The review artifact must contain these structured fields:

- `schema_version`
- `task_id`
- `repository_id`
- `base_commit`
- `reviewed_commit`
- `diff_sha256`
- `reviewer_id`
- `reviewer_role`
- `implementer_ids`
- `independence_attestation`
- `decision`: exactly `APPROVE` or `REJECT`
- `rationale`
- `findings`: list of objects containing `id`, `severity`, `gate`, `location`, `description`, `required_action`, `status`, and `evidence_refs`
- `gate_results`: one object per required gate containing `gate`, `status`, `rationale`, and `evidence_refs`
- `evidence_refs`: list of objects containing `id`, `uri`, `sha256`, `repository_id`, `commit`, `command`, `exit_code`, `environment`, and `seed`
- `reviewed_at`: UTC timestamp

For non-execution evidence, use explicit null values for execution-only fields and explain applicability in the referring gate rationale. Empty findings are allowed only with an explicit no-findings rationale and complete gate evidence.

`APPROVE` requires all required gates to pass and no unresolved blocking findings. A waived gate is not a passed gate and must not produce a review `APPROVE`.

Approval binds only to `reviewed_commit` and its recorded base/diff. Amendments, rebases, additional commits, or a changed integration result invalidate approval for that new candidate. Repeat affected checks and obtain a new review bound to the new revision. Reviewers do not edit the candidate; requested fixes return to the implementer.

### 11.3 Failure and degraded-mode behavior

On failure, stop affected work, preserve real execution evidence, and record the blocked reason, candidate identity, pending obligations, and recovery owner. Do not manufacture successful records or silently substitute roles.

| Failure | Required behavior |
|---|---|
| Required reviewer unavailable | Attempt dispatch and retain the actual failure. Set `BLOCKED_REVIEW`. Read-only analysis and evidence preservation may continue; no additional implementation attempts, acceptance, push, or merge. Request another qualified independent reviewer or a human exception. Restoration requires successful independent review of the current candidate, not merely restored service availability. |
| Delegation billing failure | Stop the failed lane and dependent work; retain the error and record the failure. The manager must not inherit prohibited implementation or specialist work. Only already-authorized, dependency-independent work may continue. Request restored service or explicit human authorization naming the substitute actor, role, scope, and duration. Role substitution does not waive independent review or other gates. Resume only after a successful real dispatch or authorized reassignment. |
| Authoritative evidence write fails | Stop acceptance and further mutating work. Preserve raw outputs and the failed write details in a durable local outbox if possible. The outbox is pending delivery, not a canonical PM-1 trace, failure record, or QMS record. If durable storage also fails, stop all work except safe shutdown and notify the human. Retry through the canonical writer, verify read-back, reconcile duplicate submissions, and independently validate revision binding before unblocking. Do not mark a write successful because it was queued. |
| Memory archive unavailable | Record the outage and queue the actual knowledge content durably with task/revision identity and delivery status. Already-authorized work may continue only while authoritative evidence remains writable and queued content can be preserved. Acceptance remains blocked by Rule 10 unless a scoped human archival-deferral exception exists. On restoration, file the queued content, verify retrieval, and record the receipt; never claim queued content is archived. |
| Crash during change | Freeze acceptance and mutation on restart. Run Rule 9 recovery, inspect worktree/index/untracked files, identify the last durable checkpoint, and reconcile traces and pending writes. Report dirty files and uncertainty; record the resume, retry, or abandon decision before proceeding. Never infer tests passed or records were delivered from an interrupted process. Reconstruct the actual candidate, rerun interrupted or uncertain checks, and obtain revision-bound review. Abandonment must preserve evidence and must not be recorded as successful completion. |

Record actual failures under Rule 2 and process violations under QMS requirements. If those writers are unavailable, apply the authoritative-evidence failure procedure to those records too. Recovery closes pending delivery obligations only after verified canonical delivery.

### 11.4 Mandatory verifier versus Oracle escalation

**Independent verifier dispatch and review are mandatory for every L2+ change.** Routine work, low risk, exhausted budget, or successful self-tests do not remove this floor.

**Oracle escalation is a separate gate.** It is mandatory for the triggers listed above. Outside those triggers, it is optional and may be cost-gated by the orchestrator. Skipping optional Oracle consultation does not waive verifier review.

One qualified independent reviewer may satisfy both verifier and Oracle gates only if explicitly assigned both responsibilities and the review records both sets of checks. Merely consulting Oracle does not constitute candidate approval.

### 11.5 Human-only exceptions

Agents may request exceptions but cannot issue, renew, broaden, or approve them. Silence, budget limits, prior approvals, and tool failure are not authorization.

Only an authenticated human authority, through an approval channel agents cannot self-issue, may:

- Authorize a specific role substitution.
- Defer memory archival with a deadline and reconciliation owner.
- Waive a named review, test, or mandatory Oracle gate for a specific candidate and acceptance action, explicitly accepting the residual risk.

Before relying on an exception, store it in authoritative QMS evidence with the human identity, task/repository identity, exact candidate commit, affected gate or role, reason, residual risk, permitted action, compensating controls, expiry, and recovery owner. Verify its authenticity independently of the implementer. If authoritative storage or approval verification is unavailable, remain blocked.

A review waiver does not create an `APPROVE`. Keep the review absent or `REJECT`, as applicable, and record the human disposition separately as `ACCEPTED_WITH_EXCEPTION`. It does not authorize push or merge unless those actions are explicitly approved.

No exception under this section permits fabricated evidence, implementer self-approval, reuse of stale approval, misrepresentation of a failed gate, or treating undelivered authoritative evidence as delivered. Other protected-resource prohibitions remain unchanged. Exceptions expire on revision change or their stated deadline, whichever occurs first; recovery obligations persist until reconciled.
