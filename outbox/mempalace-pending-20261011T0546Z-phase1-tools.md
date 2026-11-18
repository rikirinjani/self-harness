# MemPalace pending queue — filed 2026-10-11T05:46Z (fixer session)

Status: MemPalace MCP drawer interface unavailable in this session's toolset
(only the miner CLI exists locally). Queued durably per RULES Rule 11.3;
delivery owner: next session with mempalace MCP access (or the operator).

## Drawer 1 — projects/dr-benchmark-phase1
- Wing: projects, Room: dr-benchmark (new VPS)
- The 7 Phase 1 helper tools live in /opt/Deers-Rock/tools/ with shared dbutil.py
  (mysql CLI via MYSQL_PWD env + stdin; NO python MySQL driver on-box).
- Session-scope gotcha: dbutil.execute() = one mysql process = one session;
  SET FOREIGN_KEY_CHECKS=0 must be batched INTO the same stdin string as the
  INSERT or it silently does not apply (cost 2 failed attempts).
- dokter.kd_dokter FKs pegawai.nik (Khanza quirk); dump ships with FK
  violations (loaded checks-off), so master-row inserts use session-scoped
  checks-off + minimal columns; missing pegawai mirrors are inert.
- SSH key for the VPS: C:\Users\think\AppData\Local\Temp\opencode\newvps\id_ed25519_newvps
  (pub ...IDrwRTjeOKej... root@ubuntu) — NOT ~/.ssh/id_ed25519 (task brief's
  path was wrong; key lives in temp, may be cleaned — re-provision if lost).
- DR export truth: DR visits = no_rkm_medis LIKE 'DR%' (354), seed = numeric
  rkm; no_rawat '2026/10/%' alone matches BOTH (was the leak). Export now at
  /opt/simrs-khanza/consumer/dr_export.sh (DR guard + procedure-only arm);
  legacy dr_export.py (operator-local root creds) unused on-box.
- The 14-pair DOC-2 reality in the shipped dump: 7 re-rolled + 7 identical
  (report's "9 re-rolled" was a different vintage); fix = MAX per pair, now
  byte-identical re-sends; consumer MAX rule proven no-op (0 pairs distinct).
- nota_jalan numbering drifts on consumer re-runs WITHOUT clean-snapshot
  restore (MAX+1 inter-visit dependency); billing VALUE rows are fully
  idempotent (3886 rows, Rp 152,876,905 stable across 3 runs).
- Orchestrator run 20261011T053833Z: Phase 0 + all Phase 1 steps PASS; stops
  at Phase 2 (wire_icd10_content_mapper.py / build_dr_charge_ledger.py not
  built) — expected next work item.
