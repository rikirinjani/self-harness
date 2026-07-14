# Feature Development Workspace

## Layers
- Layer 0: RULES.md — hard constraints
- Layer 1: Index (this file) — stage routing
- Layer 2: Stage CONTEXT.md — per-stage contracts
- Layer 3: `_config/` + `shared/` — reference material
- Layer 4: `stages/*/output/` — working artifacts

## Stages
| # | Stage | Contract | Human gate? |
|---|-------|----------|-------------|
| 01 | analysis | Research & spec | Yes |
| 02 | plan | Architecture & tasks | Yes |
| 03 | implement | Build & test | No |
| 04 | review | Quality & audit | Yes |

## Execution
```bash
# Run a single stage:
pm1-workspace run feature-dev --stage 01

# Run full pipeline with gates:
pm1-workspace run feature-dev --all
```
