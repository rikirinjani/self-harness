# Pending MemPalace drawers (delivery queue — NOT archived yet)

Queued by: fixer agent, 2026-10-06 (mempalace CLI unavailable in shell environment)
Owner: orchestrator (re-file via mempalace_mempalace_add_drawer when tool available)

## Drawer 1 — projects/deers-rock-epic-ix (ADR-015 Phase 1 landing)

- Wing: projects, Room: deers-rock-epic-ix
- Commit: 796c5b2 on main (base fa00d4a). tsc clean; suite 284 passed + 1 skipped.
- Landed: item price tables (src/engine/price-tables.ts); per-day room billing
  from roomClassAtAdmission stamp (idempotent via lastRoomDayBilled, final
  partial day at discharge, min 1) — fixes F-A; cashier flips charge.paid on
  Payment creation (D9); dialysis/radiotherapy/ED-acuity/specialty/respiratory
  now billed at per-event hooks (D7).
- RECALIBRATION DATA: 1000-tick soak (50 patients, seed 42) median CCR 0.060 —
  OUTSIDE 0.7–1.3 band, structural not pricing: inpatient LOS 3–7 sim-days
  (4320–10080 ticks) ⇒ zero inpatient claims at 1000 ticks; paid-BPJS pool is
  all short ED/outpatient encounters vs full INA-CBG tariffs. Confirmed at
  3000 ticks: CCR 0.073, 189 room charges, still 0 inpatient discharges.
  Charge mix at 3000 ticks: dialysis 1.6B / surgery 1.2B / radiotherapy 1.0B
  dominate (pre-existing cadence now priced; dialysis re-sessions every ~10
  ticks per renal patient — throttle candidate). Payments=0 (paid BPJS claims
  carry responsibility 0; payer mix Phase 3).
- Deviations: ChargeCategory union +dialysis +radiotherapy (additive, no
  exhaustive consumers); respiratory activation fee at BOTH creation sites
  (respiratory.ts + ai-doctor.ts; nothing ever sets status="active").
