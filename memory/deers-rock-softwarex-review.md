# [Draft Detective] - [Deers Rock - SoftwareX]

## Review Files
| Round | File | Verdict | Score |
|:------|------|---------|:-----:|
| R1 | `[Draft Detective] - [Deers Rock - SoftwareX].md` | Minor Revision | 7/10 |
| R2 | `[Draft Detective] - [Deers Rock - SoftwareX] - R2.md` | Accept w/ Minor Revisions | 8/10 |
| R3 (orig) | `[Draft Detective] - [Deers Rock - SoftwareX] - R3.md` | Accept (too generous) | 9/10 |
| R3 (corrected) | `[Draft Detective] - [Deers Rock - SoftwareX] - R3.md` | Major Revision (merged blind review) | 6/10 |
| R4 | `[Draft Detective] - [Deers Rock - SoftwareX] - R4.md` | Minor Revision | 8/10 |
| **Target** | — | **Accept (projected after R5 polish)** | **9/10** |

## Score Trajectory
```
7 (R1) → 8 (R2) → 9 (R3 orig, too generous) → 6 (R3 corrected, blind review merge) → 8 (R4)
```

## Context
Pivot from original clinical paper to SoftwareX software-description format.
Paper B proposes architecture; Paper C will validate if algorithm supports full experiment.

## Issues Tracked Across All Rounds

### Resolved
| # | Issue | Round Resolved |
|---|-------|:---:|
| 1 | §4 framing as functional demo vs clinical results | R2 |
| 2 | Feature comparison table added (Table 1) | R2 |
| 3 | Cultural calendar multipliers sourced | R2, tightened R4 |
| 4 | Experiment scale limitation acknowledged | R2 |
| 5 | Generalization claims properly bounded | R2 |
| 6 | Event sourcing references added (Fowler, Young) | R3 |
| 7 | Figures rendered (not placeholders) | R3 |
| 8 | Mortality removed, LOS censoring correctly explained | R4 |
| 9 | FHIR row changed to "Partial" with footnote | R4 |
| 10 | Test coverage documented (69 tests, 13 suites) | R4 |
| 11 | Metadata complete (no placeholders) | R4 |
| 12 | HOE circularity dropped | R4 |
| 13 | Agent language: "deterministic clinical rules" instead of "clinical constitution" | R4 |

### Open (R4 → R5 polish)
| # | Item | Effort |
|---|------|--------|
| A | Table 1: add footnotes for "Modular handler chain" and "Disaster scenario engine" rows | 5 min |
| B | N=10 framing: "functional demonstration, not distributional claims" | 3 min |
| C | Snapshot interval: align text (20 ticks) with Figure 1 (100 ticks) | 5 min |
| D | Optional: cut §6 generalization or move to Future Directions | 3 min |

## R3 Correction Notes
My original R3 (Accept 9/10) was corrected after a blind reviewer flagged 8 issues I missed:
- LOS max as censoring artifact (916-992 ≈ simulation boundary)
- Table 1 FHIR row dishonesty
- Figure 1 raw Mermaid source, not rendered
- HOE architecture self-referential
- Performance scaling math (5.5x for 2x ticks invalidates 50k-tick claim)
- No test coverage for clinical rules
- Mortality advertised but not measured
- Metadata block incomplete

Score dropped from 9/10 to 6/10. This correction was recorded as a process failure at `C:\Users\think\self-harness\failures\`.

## Blind Review Quality Assessment
The blind reviewer was stricter and more thorough than my initial passes. Key strengths:
- Caught the LOS/censoring misinterpretation (methodology error)
- Applied a honesty test to Table 1 that I failed to apply
- Did the performance scaling arithmetic I skipped
- Noticed Figure 1 was raw source code

This is now reflected in my review discipline going forward.
