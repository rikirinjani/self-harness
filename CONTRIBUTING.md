# Contributing to Self-Harness

Thank you for contributing. This project implements a self-improving agent ecosystem
governed by a formal Constitution. All contributions must respect its rules.

## Constitutional Constraints (Read First)

Contributions must not violate:

- **C-02:** All harness modifications require human approval. External suggestions
  are advisory — I (the repo owner) am the human approver.
- **C-04:** Human-authored benchmarks may not be modified by agents. If you suggest
  a benchmark change, explain why and I'll evaluate it.
- **C-06:** No proposal may weaken constitutional protections.

Full text: [constitution.md](constitution.md)

## How to Contribute

### 1. Report a Weakness (Agent Failure Pattern)

If you notice a recurring failure pattern in your own OpenCode usage that matches the
Self-Harness paradigm, open a **Weakness Report** issue.

Include:
- The agent type (explorer / fixer / designer / librarian / oracle / observer)
- The failure pattern — what goes wrong, how often
- Execution trace summary (what steps led to failure)
- Verifier signal (how you know it failed)

→ Use the [Weakness Report template](.github/ISSUE_TEMPLATE/weakness-report.md)

### 2. Review a Proposal

When a candidate harness edit is under evaluation (Phase 6), you can provide independent
blind evaluation. This is one of the most valuable contributions — it directly feeds the
Validator Agreement Rate (C-07).

→ Use the [Proposal Feedback template](.github/ISSUE_TEMPLATE/proposal-feedback.md)

### 3. Suggest a Benchmark

If you have a task that would make a useful benchmark for measuring agent performance,
open a **Benchmark Suggestion**.

Include a clear task description, success/failure criteria, and which agent type it
targets.

→ Use the [Benchmark Suggestion template](.github/ISSUE_TEMPLATE/benchmark-suggestion.md)

### 4. Propose a Harness Edit

Proposals must follow the formal schema:
- `weakness_id` — which weakness it targets
- `old_value` — current harness state
- `new_value` — proposed change
- `expected_benefit` — concrete, quantified
- `risk_assessment` — honest about downsides

→ Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## Evaluation Process

Every proposal goes through this pipeline before deployment:

```
Submit → Validator (benchmark) → Human Review → Accept/Reject
```

The Validator runs the benchmark suite against both current and proposed harness.
You can see current benchmark scores in `ops/dashboard.md`.

## Scoring Rubric

All contributions are evaluated against the 8 Universal Quality Axes
(Constitution §2.1):

| Axis | Question |
|------|----------|
| A Correctness | Can every claim be verified? |
| B Completeness | Does it address all requirements? |
| C Clarity | Is it followable by newcomers? |
| D Reasoning | Does the logic hold? |
| E Precision | Are claims quantified? |
| F Efficiency | Is it concise? |
| G Actionability | Can I act on this? |
| H Faithfulness | Grounded in evidence? |

To ship: all axes ≥4. See constitution §2.7 for full threshold rules.

## Code of Conduct

- Be specific. Vague feedback is not actionable.
- Distinguish observation from interpretation.
- If you're unsure about something, say so — don't hedge without flagging it.
- This is an experimental research project. Breakage is expected.

## License

Currently unlicensed — all rights reserved. By contributing, you agree that your
contributions may be used under the same terms as the project at the owner's
discretion.
