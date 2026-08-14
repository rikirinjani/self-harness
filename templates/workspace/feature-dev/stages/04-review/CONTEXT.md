# Stage 04: Review

## Inputs
| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../03-implement/output/` | All | Code + tests |
| Skill: code-review | `~/.config/opencode/skills/code-review-and-quality/SKILL.md` | Body | Review criteria |
| Skill: code-simplify | `~/.config/opencode/skills/code-simplification/SKILL.md` | Body | Simplicity check |

## Process
1. Review code against quality criteria
2. Run simplification pass
3. Run full test suite
4. Update trace + write summary
5. Present for human approval

## Outputs
| Artifact | Location | Format |
|----------|----------|--------|
| Review report | `output/review.md` | Markdown |
| Trace | `self-harness/traces/` | PM-1 |

## Audit
- [ ] No regressions?
- [ ] Code review passes?
- [ ] Simplification applied where warranted?
- [ ] Trace written?

## Completion
Workspace complete. Human approves merge.
