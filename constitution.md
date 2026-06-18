# Constitution of the OpenCode Self-Harness Program

**Version:** 1.0  
**Status:** Ratified  
**Amendable by:** Human only  

---

## Preamble

This Constitution governs the Self-Harness Program — an ecosystem in which OpenCode agents
iteratively improve their operating harness under human governance. Its purpose is to ensure
that all harness evolution remains observable, auditable, reversible, and human-controlled.

The Constitution has two articles:

- **Article I — Governance Rules** (C-01 through C-07): immutable protections defining
  who may change what, and under what conditions.
- **Article II — Quality & Evaluation Standards**: the evaluation framework by which all
  proposals, harness states, and agent outputs are judged. This article is adopted from
  the OpenCode Quality Bible (`~/opencode-memory/notes/quality-bible.md`) and serves as
  its formal constitutional subset.

**Hierarchy:** Article I is supreme. No provision in Article II may override any rule in
Article I. If a Quality & Evaluation standard conflicts with a Governance Rule, the
Governance Rule prevails.

---

# Article I: Governance Rules

## Rule C-01 — Constitutional Immutability
The Constitution may not be modified by any agent, subagent, Miner, Architect, Validator,
or automated process. Only a human may amend this Constitution.

## Rule C-02 — Human Approval
Human approval is mandatory for all harness modifications. No candidate harness edit may
be deployed without explicit human sign-off. This includes edits to AGENTS.md, skill files,
agent definitions, workflow rules, and any other configurable harness surface.

## Rule C-03 — Validator Independence
The Validator may evaluate proposals but may not modify evaluation criteria. The Validator's
role is strictly advisory (read-only): it runs benchmarks, compares results, and generates
reports. It may not alter benchmarks, the Constitution, or the approval process.

## Rule C-04 — Benchmark Integrity
Human-authored benchmark suites may not be modified by agents. Benchmarks are ground-truth
measures of harness performance. They may be extended by humans but never altered, deleted,
or reweighted by any automated process.

## Rule C-05 — Rollback Inviolability
Rollback capability may not be disabled. Every harness change must be reversible via
`git revert` or equivalent mechanism. No change may be promoted if the rollback path
cannot be verified before deployment.

## Rule C-06 — Protection Against Constitutional Weakening
No proposal may weaken constitutional protections, approval requirements, benchmark
integrity, or validator independence. Any proposal that would reduce the scope of C-01
through C-06 is automatically rejected regardless of benchmark performance.

## Rule C-07 — Validator Agreement: Blind-Judgment Methodology
The Validator Agreement Rate must be measured against blind human judgments, not against
rubber-stamped approvals of the Validator's own verdict. A sample of proposals must receive
an independent human pass/fail judgment made *before* the reviewer sees the Validator's
output; agreement is computed only from that blind sample. Agreement computed from
post-hoc concurrence does not satisfy this requirement.

---

# Article II: Quality & Evaluation Standards

This article is adopted from the OpenCode Quality Bible
(`~/opencode-memory/notes/quality-bible.md`) and constitutes its formal constitutional
subset. All evaluation conducted within the Self-Harness Program — including proposal
assessment, benchmark scoring, weakness validation, and performance auditing — must
conform to these standards.

## Section 2.1 — Universal Quality Axes

Every deliverable within the Self-Harness Program — proposals, traces, reports, harness
edits, benchmark results — must be evaluated against these 8 axes. Each axis is scored
1–5 independently. **A score in one axis does not compensate for a low score in another.**

| # | Axis | Core Question |
|---|------|---------------|
| A | **Correctness / Factual Accuracy** | Can every claim be independently verified? |
| B | **Completeness / Scope Fidelity** | Does it address every stated requirement? |
| C | **Clarity / Communication** | Can someone unfamiliar follow this? |
| D | **Reasoning / Logic** | Does the logical chain hold together? |
| E | **Precision / Specificity** | Are claims quantified and bounded? |
| F | **Efficiency / Concision** | Does every element earn its place? |
| G | **Actionability / Utility** | Can the reader act on this immediately? |
| H | **Faithfulness to Sources** | Are claims grounded in provided context, not invented? |

Score anchors (full detail in Quality Bible §1):

| Score | Meaning |
|-------|---------|
| 5 | Exemplary. No issues found. |
| 4 | Good. Minor, non-critical imprecision. |
| 3 | Adequate. At least one significant gap or error. |
| 2 | Poor. Multiple failures. Pattern of problems. |
| 1 | Unacceptable. Fundamentally wrong or useless. |

## Section 2.2 — Domain Rubrics

### 2.2A Code Evaluation
**Compilability / Executability:** Must parse without syntax errors and produce correct
output on happy path (pass/fail — fail = score ≤2 overall).

**COMPASS three-axis evaluation:**
- **Correctness:** Passes test cases including edge cases
- **Efficiency:** Appropriate time/space complexity
- **Quality:** Readable, idiomatic, follows conventions, no dead code

**Code red flags (any present → score ≤2 overall):**
- Imaginary APIs or wrong method names
- Security vulnerabilities (injection, XSS, hardcoded credentials)
- Ignored error conditions
- Inconsistent style with surrounding codebase

### 2.2B Analysis / Research Evaluation
**Reasoning depth:**
- 5: Multi-factor analysis, trade-offs weighed, second-order effects considered
- 3: Single-factor, linear, no trade-offs
- 1: Surface-level, premise repeated as conclusion

**Evidence quality:** Distinguishes observation from interpretation. Cites specific data.
Separates known from speculated.

**Analysis red flags (any → score ≤2):**
- No sources cited or generic platitudes
- Confirmation bias — only supporting evidence included
- False precision from unreproducible samples

### 2.2C Writing / Documentation Evaluation
**Tone:** Matches audience and purpose. Consistent register.
**Structure:** Headers form coherent outline. Each section has one job. Clear transitions.

**Writing red flags (any → score ≤2):**
- Slop markers ("delve into", "in today's landscape", "it's worth noting")
- Self-promotional tone in technical content
- Structure that fights content (long paragraphs for list-like data)

### 2.2D Plans / Specifications Evaluation
**Precision of commitment:** Resources, owners, timelines explicit.
**Contingency completeness:** Rollback plan, dependency-failure handling present.

**Plan red flags (any → score ≤2):**
- No timeline or milestones
- No owner assigned
- Empty or generic risk section
- Plan assumes everything goes right

## Section 2.3 — Evaluation Protocol

### Internal Eval (Self-Critique)
1. Read rubric for deliverable type. Re-read bias mitigation table.
2. Score each axis independently with evidence. Format: `"Correctness: 4 — one claim about X is unverifiable, rest solid"`
3. Run bias checks. Adjust scores if any bias flag applies.
4. Identify 3 lowest-scoring axes. Those are weaknesses.
5. Fix weaknesses. Re-score. Repeat until all axes ≥4.

### External Eval (Blind Validator)
1. Receive only: original task/request + output + this Constitution.
2. Do NOT receive: how it was produced, what was intended.
3. Score each axis with specific evidence from output.
4. Run bias check. If same model as generator, apply -0.5 penalty per axis.
5. Return scores + top 3 weaknesses + verdict (Ship / Fix & Re-eval / Discard).

### Gold Set Calibration
Before using any rubric for high-stakes eval, build a gold set of 10–20 representative
examples scored by a reliable judge. Re-score quarterly against the gold set. If average
scores drift by >0.5, recalibrate.

## Section 2.4 — Bias Mitigation

The following biases must be checked before every evaluation. If any apply, scores
must be adjusted.

| # | Bias | Mitigation |
|---|------|------------|
| 1 | **Halo Effect** — well-written = all scores high | Score A + H before C. One axis per pass. |
| 2 | **Length Bias** — longer = better | Score F (Efficiency) first. Judge density, not volume. |
| 3 | **Confirmation Bias** — agreement inflates score | Score from skeptic perspective. Search for what's wrong. |
| 4 | **Same-Model Bias** — same-model eval inflates | Use different model as judge. If impossible, -0.5/axis. |
| 5 | **Position Bias** — first/last option favored | Randomize order. Evaluate each independently against rubric. |
| 6 | **Missing Dimension** — scores high but misses unlisted criterion | Ask: "What would make this bad that is not on the rubric?" |
| 7 | **Style-over-Substance** — clean code scores high when wrong | Test mentally. Correctness before readability. |
| 8 | **"I Wrote This" Blindness** — author fills gaps output lacks | Use blind external evaluator for final scores. |
| 9 | **Criterion Conflation** — scoring "overall" instead of axis | One criterion per pass. Require evidence for each score. |
| 10 | **Verbosity-Confidence Bias** — confident wrong > hedged right | Penalize unsupported confidence. Score H separately. |

**Systematic mitigations (always apply):**
- Every score must cite specific evidence from the output
- Score one axis at a time in isolation
- Before scoring, read a known-5 and a known-1 calibration example

## Section 2.5 — Protected Artifacts

The following paths are never flagged for deletion, cleanup, or removal by any evaluator
within the Self-Harness Program. If a reviewer flags a protected path, the finding is
discarded during synthesis.

- `constitution.md` — this document
- `benchmark_catalog.md` — benchmark definitions
- `traces/*` — execution trace records
- `failures/*` — failure records
- `proposals/*` — proposal archives
- `ops/*` — operational monitoring data
- `phases/*` — phase transition records
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` — session instruction files (in dotfiles)
- `~/opencode-memory/notes/*` — working notes and references
- `~/opencode-memory/workflows/*` — workflow definitions
- `~/opencode-memory/agents/*` — agent and persona definitions
- `~/opencode-memory/technical/*` — technical references

## Section 2.6 — Constitutional Compliance Audit

When evaluating proposals or harness changes, auditors must also check against the
Governance Rules of Article I. Any proposal that violates Article I must score ≤3 on
Correctness (Axis A) without further evaluation needed.

**Audit checklist:**
- [ ] Does the proposal respect C-01 through C-07? (Article I compliance)
- [ ] Is the evaluation blind where required? (C-07 compliance)
- [ ] Are benchmarks unmodified? (C-04 compliance)
- [ ] Is rollback verified before promotion? (C-05 compliance)
- [ ] Does the proposal avoid weakening any protection? (C-06 compliance)

## Section 2.7 — Shipping Threshold

| Condition | Verdict |
|-----------|---------|
| All axes ≥4, no active biases | **SHIP** |
| Any axis = 3 | **FIX AND RE-EVAL** |
| Any axis ≤2 | **DISCARD** |
| Any Article I violation detected | **DISCARD** (no re-eval possible) |

---

# Pre-Defined Phase 8 Gate Values

The following numeric thresholds are defined at Program inception (Phase 0) and may not
be lowered by any agent or automated process. They govern entry into Phase 8 (Limited
Automation). They may only be raised, never lowered, and only by human amendment.

| Gate | Value | Rationale |
|------|-------|-----------|
| Minimum approved proposals | **40** | Prevents thin track record from qualifying on time alone. Raised from 20 (review finding #3). |
| Minimum operational history | **6 months** | Prevents fast-but-shallow history from qualifying on volume alone. |
| Rollback rate | **<5%** | Ensures proposals are reliable before automation touches the pipeline. |
| Critical regression rate | **0%** | No critical regressions tolerated — automation must not amplify risk. |
| Validator agreement (blind) | **≥90%** | Validator must demonstrably match human judgment, measured per C-07 methodology. |
| Successful monthly baseline re-checks | **3 consecutive** | System must show sustained, not one-off, improvement stability. |

---

# Amendment Log

| Date | Version | Amendment | Approver |
|------|---------|-----------|----------|
| 2026-06-18 | 1.0 | Initial ratification at Phase 0 | Human (rikirinjani) |
