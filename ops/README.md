# Operations

Operational monitoring, drift detection, and health dashboard for the Self-Harness Program.

## Files

- `dashboard.md` — Auto-updated program health dashboard (Phase 7)
- `drift_monitor.py` — Drift detection script (Phase 7)
- `run_health_check.py` (in `tools/`) — End-to-end health check
- `thresholds.json` — Configurable warning/critical thresholds
- `alerts/` — Generated drift alerts
- `freeze_watch.json` — Emergency freeze condition tracking

## Status

Phase 7 — active since 2026-09-14.

Run the health check:

```bash
python tools/run_health_check.py
python ops/drift_monitor.py
```

Active thresholds are in `ops/thresholds.json`.
