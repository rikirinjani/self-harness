# Stage 01: Analysis

## Inputs
| Source | File/Location | Section/Scope | Why |
|--------|--------------|---------------|-----|
| User request | `_config/request.md` | Full file | Source material |
| Project conventions | `../../../../_config/common/design-system.md` | All | Style/pattern guide |

## Process
1. Read the request and understand scope
2. Research existing codebase patterns via explorer agent
3. Identify dependencies, risks, and effort
4. Write analysis output
5. Run stage audit

## Outputs
| Artifact | Location | Format |
|----------|----------|--------|
| Analysis | `output/analysis.md` | Markdown |
| Risk register | `output/risks.md` | Markdown |

## Audit
- [ ] All requirements captured?
- [ ] Dependencies identified?
- [ ] Risks scored (likelihood × impact)?
- [ ] Effort estimated with confidence range?

## Next
After review, run: `pm1-workspace run feature-dev --stage 02`
