# MemPalace outbox — queued drawer (delivery pending)
- queued_at: 2026-10-12T05:40Z (UTC)
- task: fixer-phase67-tools
- reason queued: mempalace MCP add-drawer tool not available in this session; CLI lacks add-drawer subcommand
- destination: projects / dr-khanza-benchmark
- reconciliation owner: next session with mempalace MCP access

## Content (drawer 1: phase67-tools)

Phase 6/7 tools complete on VPS (run Bseries_20261012T045027Z in flight, B3 consumer running):

1. build_benchmark_report.py — builds internal (BENCHMARK_REPORT.md) + publishable
   (BENCHMARK_REPORT_publishable.md) reports from run-dir artifacts; finds G1/replay/Jasper
   evidence in history run dirs (pattern-priority, run-dir first); publishable is composed
   from structured data only and self-verifies vs the orchestrator scrub grep — validated
   0 matches on a scratch copy (B1=PASS B2=PASS, overall ALL PASS).
2. scrub_publishable.py — in-place idempotent scrubber: all IPv4 -> <ip> (box IPs ->
   <vps-host> at runtime), benchmark_pw/EnkripsiAES/Bar12345/sayangsamakhanza/usere ->
   tokens; dirty-file test: 9 replacements, orchestrator grep 0 matches, rerun 0 (idempotent).
3. burst_test.py — Phase 7 optional 5x burst: 3 weekdays from 2026-11-02 at weekday lambda
   1500 (5x class-C 300/day), imports generate_scale_encounters with process-local overrides
   (SEQ_BASE 900001 = no_rawat '9' marker + seed 20261103 => zero no_rawat overlap with the
   B-series '8' corpus even though sql_sik_bench_restore_clean is a logging-only stub);
   defensive: all_gates_passed != 1 -> log + exit 0; --dry-run validated (no DB).

Known limitations flagged in both reports: G2 reconcile tools scope no_rawat LIKE
'2026/10/%' so B2/B3 Nov+ rows rely on manifest+telemetry+sampled-diff coverage;
sql_sik_bench_restore_clean is a logging-only stub.

Files: /opt/Deers-Rock/tools/{build_benchmark_report.py (29,457 B), scrub_publishable.py
(4,724 B), burst_test.py (12,207 B)} — py_compile clean ×3, no warnings.
Live results tree unmodified; run_all.sh sha256 unchanged; dr-bench unit active throughout.

## Content (drawer 2: b1b2-audit, queued 2026-10-12T05:45Z)

Read-only audit of B1/B2 rungs (Bseries_20261012T045027Z): both rungs publish-grade on
reason-codes (zero gaps, GAP [CODE] plumbing exists unused), sampled drift (19/19, 54/54,
rate 0.0000), determinism-evidence substitutes (manifest sha256 75889b60…ca0d /
95eae45c…615f; no Stage-B replay hash by design), and MB/1k ratios (B1 140.5 raw;
B2 61.8 raw; marginal 21.2 MB/1k — raw figures include unknown pre-run baseline).
Latency scaling: aggregate queries (revenue_by_clinic, top_billed_visits) grew ~3.0-3.4x
with 2.94x visits while datadir grew only 1.29x; buffer pool hit 99.997%→99.996% with
pool usage 90%→100%. Four under-labeled entities to fix/footnote before publishing:
(1) billing rows_est/MB stale in top-20 tables (6,619 est vs ~483k inserted);
(2) general_log_B1/B2.log both 0 bytes — real-form SQL capture silently empty;
(3) InnoDB hit-rate is lifetime-cumulative but only slow_queries carries a
"(server lifetime)" label (and long_query_time=10s makes it blind below 10s);
(4) top_diagnoses returns rows=0 (no diagnosa rows in DR cohort) — presented as latency
only. Plus: Count B is single-sourced (B==A, labeled inline), and the shared
stageA_charge_delta_per_visit.csv is overwritten per rung (currently reflects B2/Oct only).

## Content (drawer 3: report-honest-labeling, queued 2026-10-12T05:58Z)

build_benchmark_report.py patched (43,493 B) with all 7 audit flags as footnotes in BOTH
reports + marginal MB/1k preference (21.2 MB/1k B1->B2) + Jasper depth note (engine
UNAVAILABLE, 4 reports via template-SQL fallback; PASS = extraction queries succeeded).
History lookup now falls through verdict-less artifacts. Validated: py_compile clean,
scratch dry-run shows all 7 footnotes in both outputs, publishable scrub grep 0 matches,
live run untouched, dr-bench active. Numbers in footnotes are computed from artifacts
(483,359 inserted billing rows vs est 6,619; long_query_time 10 s; max p99 1.4 s), not
hardcoded, so they stay correct when Phase 6 runs with B3 present.

## Content (drawer 4: p-chain-launch, queued 2026-10-12T10:46Z)

P1-P5 review-answer chain launched detached (systemd unit p-chain, Type=exec). Drafts
bug-fixed before launch: P2 invalid-bash/missing-report/anchor fragility; P3 working-set
awk always 0 (would have SET pool to 0 — replaced with real value capture + min(1.2xWS,
60% RAM) + 128MiB rounding + never-shrink); P4 patch 3c anchor actually missed a SPACE
before the em-dash (glyph was fine), edit-4 indent 5/7 vs actual 4/6; master PSTATUS
argv-slice bug found on first launch — unit stopped cleanly before P2's run_all.sh edit
window (verified untouched), fixed, relaunched. Builder truth-fixes 1c/1d/1e added: the
"0-byte general_log / capture NOT obtained" claims were stale once B3 got its 6.7MB
AppArmor-workaround capture — now data-driven. P1 verdict live: artifact=CONFIRMED
(interrupted first sampled-diff attempt deleted the 4 visits' rows at 06:13, died at
2027-09-21 before reaching 09-23/28, retry measured the transient unbilled state).
Prelaunch validator gates: builder sha == base, dry-run patch 10/10 + py_compile,
bash -n x6, dr-bench inactive, mysql up.

## Content (drawer 5: icd10-dx-pipeline, queued 2026-10-12T23:59Z)

ICD-10 dx pipeline implemented + validated at B1 scale. Generator --dx opt-in (default
byte-identical: no-dx sha == canonical 75889b60...ca0d); DX lines inline (consumer parser
skips them, evidence .java L194-200, consumer unchanged); write_diagnosa.py post-consumer
writer (idempotent scoped delete+insert, FK-guarded, status_penyakit NULL unfaked). Model:
tier A usage-weighted (real 62-row outpatient prevalence) + tier B accpdx=Y deterministic
subset; per-template stable sets + per-visit md5 draws. Results: 8353 dx rows, top-5 =
A01.0 2149 / I50.0 1922 / D00.0 809 / K30 376 / A01.3 170; FK 0 violations; determinism
MATCH; billing totals over dx export identical to canonical B1. Drug-basket->dx left
primary-dx-only (no grounded corpus). One bug fixed mid-run: _Random proxy lacks .sample()
-> index-set draw. Effort ~2.5h vs P5's 1.5-2 day estimate.

