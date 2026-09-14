# Self-Harness

Self-improving agent ecosystem for OpenCode, implementing the Self-Harness paradigm
(arXiv 2606.09498): an iterative Weakness Mining → Harness Proposal → Proposal Validation
loop that evolves agent configurations under human governance.

## Structure

```
self-harness/
├── constitution.md          # Governance rules + Quality & Evaluation standards
├── benchmark_catalog.md     # 20 benchmark task definitions
├── traces/                  # Execution trace records (Phase 1)
├── failures/                # Structured failure records (Phase 1)
├── proposals/               # Harness modification proposals (Phase 5+)
├── benchmarks/              # Benchmark runner scripts (Phase 2)
├── validator/               # Validator agent config + reports (Phase 3)
├── ops/                     # Operational monitoring + drift detection (Phase 7)
└── phases/                  # Phase transition records
```

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Governance Foundation | ✅ Complete |
| 1 | Observation Infrastructure | ✅ Complete |
| 2 | Benchmark Runner | ✅ Complete |
| 3 | Validator | ✅ Complete |
| 4 | Weakness Miner | ✅ Complete |
| 5 | Harness Architect | ✅ Complete |
| 6 | Controlled Evolution | ✅ Complete |
| 7 | Operations | 🔄 Active |
| 8 | Limited Automation | 🔲 Gated (40 props + 6mo) |
| 7 | Operations | 🔲 Pending |
| 8 | Limited Automation | 🔲 Gated (40 props + 6mo) |

## Constitutional Rules

- **C-01:** Constitution may not be modified by agents
- **C-02:** Human approval required for all harness changes
- **C-03:** Validator may evaluate but not modify criteria
- **C-04:** Human-authored benchmarks may not be altered
- **C-05:** Rollback capability must always be available
- **C-06:** No proposal may weaken constitutional protections
- **C-07:** Validator agreement measured by blind-judgment methodology

Full text: [constitution.md](constitution.md)
