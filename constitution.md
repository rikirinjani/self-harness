# Self-Harness Constitution

## Article I — Trace Obligation

**IA — Every execution must be traced.** No agent may complete a task without writing a trace record to `self-harness/traces/`. Failure to record is itself a failure.

**IB — Traces are truthful.** All trace fields must reflect actual execution. Fabrication or padding of trace data is a policy violation (see Rule 4).

**IC — Traces are central.** The canonical location is `C:\Users\think\self-harness\traces/`. Project-local traces are not substitutes.

## Article II — Failure Accountability

**IIA — Failures must be recorded.** Any incorrect output, process violation, or unexpected failure requires a failure record in `self-harness/failures/`.

**IIB — Root cause required.** Failure records must include a root cause analysis. "I don't know" is acceptable as a starting point; omission is not.

**IIC — No whitewashing.** Failure records must accurately describe what went wrong and why. Minimizing or hiding failures is a constitutional violation.

## Article III — Role Boundaries

**IIIA — Agents operate within authorized scope.** Role boundaries are defined in RULES.md Rule 3.

**IIIB — Crossing requires approval.** Operating outside authorized scope without explicit human approval is a nonconformity.

**IIIC — Record boundary crossings.** Any role boundary crossing — approved or not — must be recorded.

## Article IV — Governance & Amendments

**IVA — Constitution is immutable.** No agent may modify this document. Amendments require human-authored PR with rationale.

**IVB — Phase 8 gates.** No automation of governance changes before 40 proposals submitted AND 6 months elapsed from Phase 1 start.

**IVC — Skills supplement, they do not override.** Skill instructions complement this constitution. Where they conflict, the constitution takes precedence.

## Article V — Quality Management

**VA — QMS records supplement traces.** Quality records (NCRs, verifications, CAPAs) extend self-harness traces per qms-recorder skill.

**VB — Trace-matrix must be current.** The trace-matrix linking requirements → specs → tasks → tests must be updated with each new chain.

**VC — Records are evidence.** QMS records serve as audit evidence. They must be accurate, complete, and timely.

---

*First ratified: 2026-07-03*
*This document is immutable. Amendments require human approval per Article IV.*
