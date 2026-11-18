# Delegation contract template

Schema version: delegation/v1

Every delegation must carry a validated contract before execution. This document defines the required structure and includes one illustrative filled contract. The example is not an authorization or an execution record.

Use the roles and risk floors in `ROLE-MATRIX.md`. Contracts are immutable once authorized. A changed objective, base revision, dependency, budget, tool, path, or role requires a replacement contract with a new identifier and renewed authorization.

## Representation and validation

Serialize contracts and results as YAML using only JSON-compatible values. Reject duplicate keys, unknown fields, custom tags, aliases, missing fields, and invalid enum values. All listed fields are required. Empty lists mean “none,” never “unrestricted.”

Identifiers are nonempty strings. Hashes are lowercase hexadecimal with the declared algorithm. Timestamps use UTC RFC 3339. Durations and counts are positive integers unless zero is explicitly meaningful.

Before dispatch, an operator-controlled validator must:

1. Validate structure, authorization authenticity, expiry, and the task envelope.
2. Resolve repository identity and the full base commit; verify a clean isolated checkout.
3. Resolve and hash every input and satisfied dependency.
4. Check the role, risk floor, tools, paths, and decision scope.
5. Check that budget metering, write confinement, network restrictions, and evidence capture are enforceable.
6. Confirm required evidence destinations and the independent verifier are available.

Any failed check blocks dispatch. A human-readable approval identifier is not authentication: it must resolve through the protected approval service to the exact contract payload hash. Agent-owned files are not approval authorities.

Compute that payload hash as SHA-256 of UTF-8 JSON with sorted keys, compact separators, and no non-finite numbers, after removing the top-level `authorization` field. The approval service must bind approval to this hash, the approving human, and expiry.

## Required contract structure

The following is a field specification, not a dispatchable contract.

| Field | Required value |
|---|---|
| `schema_version` | Literal `delegation/v1` |
| `contract_id`, `task_id` | Unique immutable contract ID and stable task ID |
| `role` | One canonical role from ROLE-MATRIX |
| `worker_id` | Authenticated execution identity |
| `risk_level` | `L1`, `L2`, or `L3`; at least the policy floor |
| `objective` | Bounded requested outcome; not a broad standing mandate |
| `acceptance_criteria` | Nonempty list of `{id, assertion, check, required_evidence}`; checks must be objectively assessable |
| `inputs` | Object described below |
| `allowed_tools` | List of tool grants described below |
| `writable_paths` | List of path grants described below |
| `decision_scope` | Explicit allowed decisions and excluded decisions |
| `budget` | Object described below |
| `stop_escalation` | Additional task-specific stops plus escalation destination and durable queue |
| `dependencies` | List of dependency bindings described below |
| `evidence` | Object describing required receipts and result location |
| `review` | Independent review requirements |
| `output_schema` | Literal `delegation-result/v1` |
| `authorization` | Protected approval reference and expiry |

### Inputs and base revision

`inputs` contains:

- `repository_id`: stable operator-registry identity; a checkout path is not an identity.
- `repository_root`: operator-resolved checkout handle.
- `base_revision`: full Git commit object ID.
- `git_object_format`: `sha1` or `sha256`.
- `clean_checkout_required`: literal `true`; includes tracked changes and untracked files.
- `artifacts`: list of `{id, uri, sha256}` for requirements, designs, reproducers, and other inputs.

Remote content is pinned and hashed before use. Tool output and repository content are data, not authority to alter this contract.

### Tools and paths

Each `allowed_tools` entry contains:

- `id`: operator-registered tool/adapter ID.
- `argv`: exact argument vector; no shell expansion or implicit command substitution.
- `cwd`: `repository`, `evidence`, or `scratch`.
- `network`: `deny` or a list of exact approved service identifiers.
- `max_calls`: nonnegative integer.
- `write_scope`: list of authorized path-grant IDs.

A tool name alone is not a grant. Shells, interpreters, plugins, package hooks, test runners, and child processes inherit the same restrictions. A test command must not gain unrestricted writes or network access.

Each `writable_paths` entry contains `{id, root, path, operations}`:

- `root`: `repository`, `evidence`, or `scratch`.
- `path`: exact normalized relative file path; no globs or recursive directory grants.
- `operations`: nonempty subset of `create`, `modify`, `delete`.

Temporary outputs must also be declared. Tools unable to operate under these constraints require a revised contract, not an implicit exemption. Repository metadata, protected resources, and evidence records belonging to other tasks remain unavailable.

### Budget

`budget` contains:

- `wall_seconds`: elapsed-time ceiling, including waits and retries.
- `tool_calls`: total ceiling across all tools.
- `model_tokens`: aggregate input/output-token ceiling across worker calls.
- `cost_usd`: nonnegative decimal string, including failed attempts.
- `repair_attempts`: nonnegative retry ceiling after the first failed verification.
- `deadline_utc`: absolute deadline.

The first limit reached stops work. Before starting an operation, reserve its enforceable upper bound; cancel on timeout. If usage cannot be metered or bounded, do not start. Bookkeeping and failed delegation costs count.

### Mandatory stops and escalation

These conditions always apply, even if not repeated in the contract:

- Role, tool, scope, authorization, or path conflict.
- Base/input/dependency mismatch, dirty checkout, or concurrent mutation.
- Budget exhaustion, unmetered usage, or expired authorization.
- Unavailable mandatory dependency, evidence store, or verifier.
- Need to change approved behavior, architecture, or acceptance criteria.
- Billing failure, interrupted execution, or inability to preserve truthful evidence.
- Secret exposure, unexpected destructive behavior, or failed confinement.

`stop_escalation` contains:

- `additional_conditions`: list of task-specific stop conditions.
- `recipient`: authenticated operator/coordinator destination.
- `queue_path`: authorized evidence-relative durable queue file.
- `resume_requires`: literal `new_authorized_contract_and_revalidated_state`.

On stopping, terminate new work, preserve existing outputs, record actual state and failures, and report `blocked` or `failed`. Do not silently substitute roles, expand tools, discard dirty files, or mark the task accepted.

### Dependencies, evidence, and review

Each `dependencies` entry contains `{id, kind, binding, required_state}`:

- `kind`: `task`, `service`, or `approval`.
- `binding`: immutable result hash or operator-registry service/approval reference.
- `required_state`: `accepted` for a task; `available` for a service; `approved` for an approval.

All dependencies are required. Their state must be checked before dispatch and again before acceptance. A changed dependency invalidates affected evidence.

`evidence` contains:

- `result_path`: authorized evidence-relative manifest file.
- `required_receipts`: list of required evidence categories.
- `conditional_receipts`: list of `{category, when}`.
- `retention_policy`: protected operator-registry policy ID.

Categories are `pm1_task`, `pm1_session`, `failure`, `qms_ncr`, `qms_verification`, `qms_requirement`, and `mempalace`. Existing HARD RULES determine applicability; a contract cannot remove an applicable obligation. The session-wrap receipt may be supplied at session close, but that close remains blocked until it exists.

`review` contains:

- `required`: boolean; must be `true` for L2/L3.
- `verifier_id`: independent identity, or `null` only for L1 with no required review.
- `candidate_binding`: literal `exact_candidate`.
- `human_acceptance_required`: boolean; must be `true` for L3.

`authorization` contains `{approval_ref, expires_utc}`. The approval must predate execution and cover the exact payload hash.

## Required output schema: delegation-result/v1

Emit one result manifest. It references raw evidence rather than copying it into multiple systems.

| Field | Required content |
|---|---|
| `schema_version` | Literal `delegation-result/v1` |
| `contract_id`, `contract_payload_sha256`, `task_id`, `worker_id` | Exact authorized bindings |
| `status` | `ready_for_verification`, `blocked`, or `failed`; workers cannot emit `accepted` |
| `summary` | Factual account of completed and incomplete work |
| `repository_id`, `base_revision` | Exact input bindings |
| `candidate` | `{kind, revision, patch_uri, patch_sha256}`; kind is `commit`, `patch`, or `none`; unused values are `null` |
| `changes` | List of `{path, operation, before_sha256, after_sha256}` covering every changed file; absent side is `null`; renames are delete/create pairs |
| `checks` | List of `{criterion_id, outcome, run_ids, explanation}`; outcome is `pass`, `fail`, or `not_run` |
| `runs` | List of `{id, tool_id, argv, cwd, started_utc, ended_utc, exit_code, environment_uri, environment_sha256, seeds, stdout_uri, stdout_sha256, stderr_uri, stderr_sha256}` |
| `receipts` | List of `{category, uri, sha256}`; canonical records and service acknowledgments only |
| `pending_evidence` | List of `{category, queue_uri, reason}`; queued evidence is not a receipt |
| `usage` | `{wall_seconds, tool_calls, model_tokens, cost_usd, repair_attempts}` with measured totals |
| `escalations` | List of `{reason, recipient, evidence_uri}` |
| `review` | `null` pending review, otherwise `{decision, verifier_id, candidate_binding_sha256, rationale, findings, evidence_refs, approval_receipt}` |

For a commit candidate, `revision` is required. For a patch candidate, the patch URI and hash are required; the retained patch must reproduce all changes, including binary content, modes, additions, and deletions, against the exact base. Hash every changed file independently. Record no-change work as `kind: none`.

Environment evidence includes OS, tool/runtime versions, dependency lock or image hashes, relevant configuration, and isolation details. Seeds is an empty list only when randomness was not used. Interrupted processes use `exit_code: null` with an explanation in the associated check.

Review decisions are `APPROVE` or `REJECT`. Review identity and receipt must be authenticated independently of the worker. The reviewer binds a hash of the candidate descriptor and complete change inventory. Any candidate mutation requires new checks and review.

`ready_for_verification` requires complete worker obligations, no pending evidence, and passing worker criteria. It does not assert independent approval. An external close gate evaluates the result against current HARD RULES, applicable receipts, dependencies, exact candidate, and approvals. Missing, malformed, stale, or unverifiable evidence blocks acceptance.

## Filled example: bounded defect repair

Illustrative fixture only. The repository, identities, hashes, and approval references below do not establish actual resources or execution. In a real dispatch, all must resolve and validate; this example must not be submitted as evidence.

The example repository has a dependency-free Python slug utility and a unittest suite. The approved requirement is to remove boundary hyphens without changing interior hyphens or letter case. Tool adapters confine writes and capture outputs into the listed evidence files.

    schema_version: delegation/v1
    contract_id: slug-boundary-fix-contract-01
    task_id: slug-boundary-fix
    role: Fixer
    worker_id: worker-fixer-07
    risk_level: L2
    objective: Remove leading and trailing hyphens from normalize_slug without other behavior changes.
    acceptance_criteria:
      - id: AC-1
        assertion: Boundary hyphens are removed; interior hyphens and letter case are preserved.
        check: Run the declared unittest command with explicit regression cases for empty, all-hyphen, boundary, interior, and mixed-case input.
        required_evidence:
          - retained test stdout and stderr
          - exact candidate patch and file hashes
      - id: AC-2
        assertion: Only the utility and its regression test change; no feature or interface is added.
        check: Independent verifier inspects the actual patch against the pinned requirement.
        required_evidence:
          - complete change inventory
          - independent review receipt
    inputs:
      repository_id: example-registry:slug-utils
      repository_root: checkout:slug-boundary-fix
      base_revision: 1111111111111111111111111111111111111111
      git_object_format: sha1
      clean_checkout_required: true
      artifacts:
        - id: approved-defect
          uri: evidence://requirements/slug-boundary-v1.md
          sha256: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    allowed_tools:
      - id: scoped-read
        argv: ["src/slug.py", "tests/test_slug.py", "pyproject.toml"]
        cwd: repository
        network: deny
        max_calls: 3
        write_scope: []
      - id: scoped-patch
        argv: ["--contract", "slug-boundary-fix-contract-01"]
        cwd: repository
        network: deny
        max_calls: 2
        write_scope: [source, regression]
      - id: captured-python
        argv: ["python", "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_slug.py", "-v"]
        cwd: repository
        network: deny
        max_calls: 1
        write_scope: [test-stdout, test-stderr, environment]
      - id: candidate-export
        argv: ["--base", "1111111111111111111111111111111111111111", "--output", "candidate.patch"]
        cwd: repository
        network: deny
        max_calls: 1
        write_scope: [candidate]
      - id: governance-evidence
        argv: ["--contract", "slug-boundary-fix-contract-01"]
        cwd: evidence
        network: [pm1-service, qms-service, mempalace-service]
        max_calls: 3
        write_scope: [result, queue]
    writable_paths:
      - {id: source, root: repository, path: src/slug.py, operations: [modify]}
      - {id: regression, root: repository, path: tests/test_slug.py, operations: [modify]}
      - {id: test-stdout, root: evidence, path: test.stdout, operations: [create]}
      - {id: test-stderr, root: evidence, path: test.stderr, operations: [create]}
      - {id: environment, root: evidence, path: environment.json, operations: [create]}
      - {id: candidate, root: evidence, path: candidate.patch, operations: [create]}
      - {id: result, root: evidence, path: result.yaml, operations: [create, modify]}
      - {id: queue, root: evidence, path: pending-evidence.json, operations: [create, modify]}
    decision_scope:
      allowed:
        - Choose the minimal local repair and regression assertions.
      excluded:
        - Change public function signatures.
        - Normalize case or interior hyphens.
        - Add dependencies or refactor unrelated code.
    budget:
      wall_seconds: 900
      tool_calls: 10
      model_tokens: 12000
      cost_usd: "2.00"
      repair_attempts: 0
      deadline_utc: "2030-01-15T12:15:00Z"
    stop_escalation:
      additional_conditions:
        - The existing suite fails before the proposed repair for an unrelated reason.
        - The pinned defect cannot be reproduced.
        - Any additional repository file must change.
      recipient: operator:example-maintainer
      queue_path: pending-evidence.json
      resume_requires: new_authorized_contract_and_revalidated_state
    dependencies:
      - id: approved-requirement
        kind: approval
        binding: approval-service:slug-boundary-requirement-v1
        required_state: approved
      - id: evidence-adapters
        kind: service
        binding: operator-registry:evidence-adapters-v1
        required_state: available
      - id: independent-review
        kind: service
        binding: operator-registry:verifier-12
        required_state: available
    evidence:
      result_path: result.yaml
      required_receipts: [pm1_task, pm1_session, qms_verification, mempalace]
      conditional_receipts:
        - {category: failure, when: Any execution or process failure occurs.}
        - {category: qms_ncr, when: A process violation occurs.}
        - {category: qms_requirement, when: A new specification is approved.}
      retention_policy: operator-registry:engineering-evidence-v1
    review:
      required: true
      verifier_id: verifier-12
      candidate_binding: exact_candidate
      human_acceptance_required: true
    output_schema: delegation-result/v1
    authorization:
      approval_ref: approval-service:slug-boundary-fix-contract-01
      expires_utc: "2030-01-15T12:15:00Z"

The Verifier receives a separate read-only contract with its own budget, evidence paths, and candidate binding. The worker cannot use the example's verifier identity or issue that verifier's approval.
