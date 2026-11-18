# Authoritative role and permission matrix

Version: 1.0

## Authority and scope

On explicit human adoption, this document replaces RULES.md Rule 3 and conflicting role descriptions in prompts, skills, and delegation instructions. It does not waive other HARD RULES, authorize an existing task, or assert that access controls have been deployed.

Each delegation must use `delegation-contract-template.md`. Effective permission is the intersection of:

1. This matrix.
2. The human-authorized task envelope.
3. The delegation's explicit tools, paths, and decision scope.
4. Permissions actually granted by the execution environment.

Missing permission means denied. A delegation may narrow permissions, never expand them. Conflicts, missing authorization, or unavailable enforcement block dispatch. Agents cannot authorize their own exceptions.

These documents specify policy, not an enforcement boundary. The operator must enforce tool access, filesystem scope, protected integration, and acceptance gates outside the worker's control. Until those controls exist, use supervised execution only.

## Names and identities

- **Coordinator = orchestrator = manager.** All refer to the coordination role, not an implementation role.
- **Implementer = implementation engineer = coder.** This is the ordinary code-writing role formerly assigned to Coordinator.
- **Fixer** is a restricted Implementer assignment for a specified defect, not a fallback implementation role.
- **Platform = architect.**
- **Oracle = advisor/reviewer.** Oracle may produce written advice and review artifacts, but not implementation changes.
- **Verifier** is an independently assigned acceptance-review role; Oracle may fill it only when the independence requirements below hold.
- Librarian, Explorer, and Designer retain their names.

Aliases do not grant multiple roles. Each delegation has one role. Role substitution requires a new contract and explicit human approval before the new role acts. Prior unauthorized work remains a nonconformity; approval is not retroactive.

## Path conventions

`R` is the repository root identified in the contract. `E` is an operator-managed evidence workspace outside the candidate checkout.

Paths in the matrix describe categories, not wildcard grants. Every writable file must be enumerated in the contract as a repository-relative or evidence-relative path. Creation, modification, and deletion are separate permissions. A rename requires deletion permission for its source and creation permission for its destination.

Reject absolute paths, traversal, symlink/reparse-point escapes, case-colliding paths, and paths resolving outside the selected root. Generated files are not exempt. External writes require an explicitly authorized adapter, destination, and operation.

All roles may submit truthful PM-1 traces and applicable failure, QMS, and MemPalace records through approved adapters. This does not authorize direct modification of their backing stores or alteration of prior records.

## Matrix

| Role | May-read | May-write (paths) | May-decide | Must-escalate | Forbidden |
|---|---|---|---|---|---|
| Coordinator / orchestrator / manager | Authorized requirements, task metadata, repository context, dependency status, and evidence | Enumerated `E` contract, dispatch, status, and evidence-index files only | Decompose approved objectives; assign permitted roles; schedule dependencies; stop work; request review | Architecture ambiguity; missing implementer; billing/tool failure; budget exhaustion; scope, role, or permission change; failed acceptance gate | Product code or tests; specialist research as a substitute for dispatch; architecture decisions; self-issued approvals; accepting its own implementation; bypassing close/merge gates |
| Implementer | Authorized requirements, approved design, repository files, and test evidence | Enumerated `R` implementation, test, and documentation files; enumerated `E` result files | Implementation details within approved design and acceptance criteria | New feature or design scope; public interface change not already approved; sensitive resource; required out-of-scope edit; failed dependency | Changing requirements or its own permissions; unapproved architectural decisions; self-acceptance; integration/merge |
| Fixer | Authorized defect report, reproducer, relevant code, and tests | Enumerated `R` files necessary for the specified fix and regression tests; enumerated `E` result files | Minimal repair within the agreed defect boundary | Feature request; broad refactor; architecture/interface change; inability to reproduce; additional affected paths | Adding features; unrelated cleanup; broad redesign; self-acceptance; integration/merge |
| Platform / architect | Authorized requirements, code, constraints, and research | Enumerated `R` design documents and agent/skill prompt sources; enumerated `E` design artifacts | Design choices within approved requirements; proposed interfaces and architecture | Requirement conflict; security/trust-boundary change; implementation needed; policy/permission change | Product implementation or test code; directly changing runtime permissions; self-approving its design or prompt changes |
| Librarian | Authorized documentation, references, and research tools | Enumerated `E` research artifacts; explicitly authorized `R` reference documents | Source selection; evidence quality; research conclusions | Conflicting or unavailable sources; confidential material; implementation or architectural decision requested | Code changes; architecture selection; representing unverified claims as established facts |
| Explorer | Authorized repository files, history, and read-only inspection tools | Enumerated `E` context maps and inspection reports only | What context to inspect within the assigned scope | Missing context/access; conflicting findings; requested recommendation beyond factual inspection | Repository changes; architecture or implementation decisions; presenting inference as observed execution |
| Oracle / advisor-reviewer | Authorized requirements, actual diff, design, and independently accessible evidence | Enumerated `E` advice and review artifacts only | Advice, critique, findings, and a review recommendation with rationale | Missing raw evidence; ambiguous requirements; implementation request; independence conflict | Implementation patches, production edits, or executable remediation scripts; changing requirements; accepting or merging a candidate |
| Verifier | Requirements, actual candidate diff, exact revisions, and independently accessible raw results | Enumerated `E` verification records and outputs; declared disposable test scratch paths only | `APPROVE` or `REJECT` for the exact candidate against stated criteria | Missing/stale evidence; reproduction failure; identity conflict; candidate mutation; unavailable test environment | Candidate edits; verifying its own implementation; substituting implementer claims for evidence; integration/merge |
| Designer | Authorized UI sources, interaction requirements, accessibility criteria, and visual evidence | Enumerated `R` styles, visual assets, and presentation-only markup; enumerated `E` design artifacts | Layout, typography, color, spacing, and presentation within approved behavior | Any change to event handling, state, validation, navigation, data flow, permissions, business rules, or interaction semantics; mixed presentation/logic edit that cannot be separated | Behavioral changes, including “small UI logic” fixes; bypassing accessibility criteria; self-acceptance; integration/merge |

## Decisions, review, and acceptance

- Oracle advice is an allowed output, not implementation and not an acceptance gate. “Reviews only” means no implementation authority, not silence.
- Designer may edit presentation, not behavior. A behavioral UI change goes to an Implementer or Fixer under a new contract.
- Fixer handles a named defect. Features and broader implementation go to Implementer.
- Coordinator coordinates even when a specialist is unavailable. Dependency failure never grants fallback coding permission.
- No agent role grants integration/merge authority. A human or independently protected integration service controls that operation.

Use these minimum risk floors; uncertainty escalates rather than reducing risk:

- **L1:** read-only project work; only declared evidence and disposable scratch writes.
- **L2:** any persistent project change, including documentation, presentation, tests, prompts, and skills. Independent verification is mandatory.
- **L3:** policy, permissions, credentials, security boundaries, deployment, destructive operations, or changes to the acceptance machinery. Explicit human approval and independent verification are mandatory.

An implementer cannot downgrade these floors. Oracle consultation may be optional; L2/L3 verification is not cost-optional.

A Verifier must have a distinct execution identity and context from every author of the candidate, receive requirements and the actual diff rather than only an author summary, and access raw results independently. Someone who authored the candidate's design or implementation cannot verify that same candidate. A separate agent alone is not proof of institutional independence; record shared infrastructure and limitations.

Verification binds to repository identity, task ID, base revision, candidate revision or patch hash, relevant artifact hashes, exact commands, environment, seeds where applicable, and retained outputs. Candidate changes invalidate approval. `APPROVE` requires rationale and evidence references.

## One evidence index, not four competing verdicts

Each task produces one versioned delegation result manifest as defined in the contract template. It indexes evidence; it does not replace required evidence stores or duplicate their contents.

- PM-1: execution trace references.
- self-harness: retained trace/failure references.
- QMS: required nonconformity, verification, and requirement references.
- MemPalace: required knowledge archival receipts.
- Local result manifest: bindings, outcomes, hashes, and the references above.

A worker reporting `ready_for_verification` has not closed or accepted the task. An independently enforced close gate checks required receipts, revision-bound verification, and human approvals. Path-history coverage alone is not acceptance evidence.

If a mandatory system is unavailable, retain a truthful result and a durable delivery queue in the authorized evidence workspace, mark the task `blocked`, and stop acceptance. A queued item is not a receipt. If durable recording is also unavailable, stop further work and notify the operator through the available channel. Restoration requires successful delivery, receipt validation, and rerunning affected gates.

No synthetic execution records, silent omissions, or agent-issued waivers are permitted.
