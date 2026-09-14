# Phase 7 Plan: Operations

**Status:** Active  
**Entry date:** 2026-09-14  
**Prerequisite:** Phase 6 complete  
**Duration estimate:** 1–2 weeks

---

## Goal

Keep the self-harness program healthy between improvement cycles by monitoring benchmark scores, proposal backlog, failure categories, trace hygiene, and harness rule drift. Raise alerts when pre-defined thresholds are crossed and provide an always-current dashboard.

---

## Deliverables

### 1. Drift monitor

`ops/drift_monitor.py`:
- Reads `ops/weakness_history.json` and prior dashboard state.
- Detects significant changes (thresholds below).
- Emits a JSON alert file to `ops/alerts/` when drift is detected.
- Appends a summary line to `ops/dashboard.md`.

### 2. Health check runner

`tools/run_health_check.py`:
- Runs quickly and reports program health:
  - benchmark summary (`benchmarks/run.py --summary`)
  - trace cleanliness (`tools/retrace.py`)
  - pending promotion approvals in `shadow/reports/*-awaiting-approval.json`
  - current phase statuses from `phases/*-progress.md`
  - count of uncommitted harness changes
- Exits non-zero if any critical check fails.

### 3. Operational dashboard

`ops/dashboard.md`:
- Auto-updated with latest health check.
- Sections: health summary, flagged benchmarks, weakness themes, pending approvals, recent alerts.

### 4. Phase progress tracking

`phases/phase-7-progress.md`.

---

## Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Avg benchmark diff | > 0.5 | > 1.0 |
| Failure records growth (vs last run) | +5 | +10 |
| Trace records growth | +50 | +100 |
| Pending promotions | ≥1 | ≥3 |
| Trace-clean scanner | — | dirty |
| Active harness re-validation | — | fails |

---

## Entry Criteria

- [x] Phase 6 exit gate met.
- [x] Active harness rules promoted and re-validated.
- [x] `ops/` directory exists with historical weakness data.

---

## Exit Criteria / Gate

Phase 7 is complete when:

- [x] `ops/drift_monitor.py` detects drift and writes alerts.
- [x] `tools/run_health_check.py` runs end-to-end and exits cleanly.
- [x] `ops/dashboard.md` is updated by the health check.
- [x] At least one alert or threshold-crossing event recorded.
- [x] Human approves exit.

---

## Execution Strategy

### Week 1 — Monitoring

1. Define thresholds and alert schema.
2. Build `ops/drift_monitor.py`.
3. Build `tools/run_health_check.py`.

### Week 2 — Dashboard Integration

1. Wire health check to update `ops/dashboard.md`.
2. Run health check and capture baseline alert.
3. Update README phase table and commit.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| False-positive alerts | Thresholds are configurable in `ops/thresholds.json`. |
| Dashboard grows stale | Health check is cheap enough to run every session. |
| Health check itself breaks | It reuses existing tested tools (`benchmarks/run.py`, `tools/retrace.py`). |

---

## Resources

- Weakness history: `ops/weakness_history.json`
- Dashboard: `ops/dashboard.md`
- Thresholds: `ops/thresholds.json`
- Health check: `tools/run_health_check.py`
