# Stage 03: Implement

## Inputs
| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../02-plan/output/tasks.md` | All | Task list |
| Skill: incremental-impl | `~/.config/opencode/skills/incremental-implementation/SKILL.md` | Body | Build approach |
| Skill: tdd | `~/.config/opencode/skills/test-driven-development/SKILL.md` | Body | Test approach |
| Config | `_config/` | All | Design system, conventions |

## Process
1. Implement each task incrementally
2. Write tests alongside (TDD)
3. Run tests after each increment
4. Run stage audit

## Outputs
| Artifact | Location | Format |
|----------|----------|--------|
| Code | `output/` | Source files |
| Test results | `output/test-results.md` | Markdown |

## Audit
- [ ] All tasks completed?
- [ ] All tests pass?
- [ ] No unrelated changes?
- [ ] Follows project conventions?

## Next
Run: `pm1-workspace run feature-dev --stage 04`
