# Stage 02: Plan

## Inputs
| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| Previous stage | `../01-analysis/output/` | Full files | Source material |
| Skill: spec-driven-dev | `~/.config/opencode/skills/spec-driven-development/SKILL.md` | Body | Spec format |
| Skill: planning | `~/.config/opencode/skills/planning-and-task-breakdown/SKILL.md` | Body | Task breakdown |

## Process
1. Read analysis output
2. Write technical spec (following spec-driven-development)
3. Break into tasks (following planning-and-task-breakdown)
4. Assign to agents
5. Run stage audit

## Outputs
| Artifact | Location | Format |
|----------|----------|--------|
| Technical spec | `output/spec.md` | Markdown |
| Task breakdown | `output/tasks.md` | Markdown |

## Audit
- [ ] Spec covers all requirements?
- [ ] Tasks are independent where possible?
- [ ] Dependencies explicit?
- [ ] Estimatess have confidence ranges?

## Next
After review, run: `pm1-workspace run feature-dev --stage 03`
