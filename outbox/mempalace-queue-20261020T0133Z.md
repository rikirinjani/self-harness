# MemPalace outbox — pending delivery

status: PENDING (mempalace tools unavailable in this session; no MCP memory server attached)
created: 2026-10-20T01:33Z
source task: khanza-r5 P11 (discriminating recovery checks / negative controls)
commits: 90e981d, f935b1e, f55369c (branch khanza-r5-p6, not pushed)
reconcile owner: next session with mempalace access
receipt required: yes (record retrieval proof; do not claim archived until then)

## drawer 1 — wing: projects, room: khanza-r5

P11 closed as PARTIAL. Every P10 recovery check now has a demonstrated negative
control: T1 A28' (R5_NEGCTL_BACKUP_NO_TXN), T2 pre-operation baseline
(R5_NEGCTL_SKIP_IMMEDIATE_RESTORE), T3 inventory/dropped table, T4 marker
atomic+fsync with the old fail-open path shown and beaten, T5
(R5_NEGCTL_KEEP_STALE_FLAG), T6 (R5_NEGCTL_HASH_FROM_LIVE_LATE), T7
(P11_FORCE_FAIL keeps the fixture), T8 wording with re-derived numbers
(13 tables / 21 rows / 5 non-empty). Frozen tool byte set: suite 7ecb20ef,
run_suite 0865400d, diff e2c1d2f9, hash_state d59b18fb, preservation e5d39756,
NC a3f44721, unit 73b6468f; chattr +i on the VPS, manifest sha256sum -c before
and after every run. Frozen-set results: unit 33/33, NC 5/5 across two
invocations (4/5 + clean NC1), suite 39/39 exit 0, preservation PASS, forced
failure = exactly one FAIL with fixture kept, builder reproduces live ledger
356355:a66a3a54..., live state clean at 21:12:34Z and 01:07:40Z.

## drawer 2 — wing: agentic-layer, room: evidence-integrity

Lesson: byte-freezing tools does not bind evidence when the fixture is shared.
A second agent session on the same machine and VPS re-created sik_p6f and
re-granted the benchmark account mid-stream, inverting a negative control that
had already passed. Two independent bindings are required for every
discriminating check: (a) frozen tool bytes verified immediately before and
after the run, and (b) an exclusive window on the mutable fixture, verified by
an absence precondition, not by a previous teardown. Also: the NC driver reused
an existing fixture instead of rebuilding — a driver that "reuses if present"
converts a clean precondition into an untested assumption.

## drawer 3 � wing: projects, room: khanza-r5 (appended 2026-10-23)

VPS migration complete. Replacement box labeled 'mac mini vultr' (Vultr 2 vCPU /
16 GB / 94 GB, Ubuntu 24.04.5 x86_64, IPv6-only SSH, hostname mac-mini-vultr,
alias in ~/.ssh/config, env khanza-r5/.vps-mac-mini.env). Asset verified on it:
manifest OK on-box, jar md5 25acbbbe, frozen tools OK + chattr +i, ledger hash
356355:a66a3a54 reproduced, benchmark@localhost fresh password with old-box
grants, database.xml re-encoded via PatchDbXml (classpath: consumer +
KhanzaSecurity16bit/build/classes + lib/mariadb.jar + commons-codec; ALL FIVE
xml properties are AES-encoded). results/ copied 1.3G/8633 files. Owner
decision: BOTH boxes stay live; .vps.env still targets the older vultr box.
Deferred by owner: sshd hardening on the new box (password auth still open).
