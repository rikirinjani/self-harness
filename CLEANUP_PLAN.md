# Cleanup Plan — Self-Harness Repo

**Created:** 2026-09-14  
**Scope:** Immediate housekeeping before and during Phase 3  
**Owner:** rikirinjani (human) + agent loop

---

## Cleanup Tasks

| # | Task | Priority | Estimated Effort | Rationale |
|---|------|----------|------------------|-----------|
| 1 | **Unify trace schema** — convert legacy `.pm1` traces to the planned `.json` schema, or add a parser that accepts both. | High | 1–2 sessions | Phase 1 spec expects structured JSON traces; current backlog is `.pm1`. The weakness miner needs a single format. |
| 2 | **Consolidate failure taxonomy** — ensure every `failures/*.json` record has `category`, `severity`, and `failure_signature` fields. Add a linter script. | High | 1 session | Weakness mining depends on consistent categorization. Many backlog records are missing taxonomy fields. |
| 3 | **Remove or archive transient files** — audit root-level files (`dream_prec.txt`, `eval_questions.json`, `mm_recs.txt`, `prec_summary.txt`, `preflight_out.txt`) and decide whether they belong in `state/`, `docs/`, or `.gitignore`. | Medium | 30 min | Reduces clutter and clarifies which files are canonical. |
| 4 | **Audit `.gitignore`** — add `__pycache__` (done), `.env*`, `*.log`, and any OS/editor artifacts. | Low | 15 min | Prevents accidental commits of generated/sensitive files. |
| 5 | **Consolidate `state/` directories** — merge `state/pm1-trading-benchmark/` into a single project state schema or move per-project state into a `projects/` subtree. | Medium | 1 session | The current `state/` layout is ad-hoc and hard to scan. |
| 6 | **Document branch strategy** — write `docs/branching.md` explaining `main`, `master`, `sync-phase2`, and how future phase work will branch from `main`. | Medium | 30 min | Avoids future unrelated-history merges and divergence. |
| 7 | **Archive the external temp snapshot** — delete `C:\Users\think\.local\share\opencode\tmp-sh\local-backlog` now that the backlog is committed. | Low | 5 min | It was a safety copy; keeping it creates duplication risk. |

---

## Suggested Order

1. Do #4 first (`.gitignore`) — it is small and prevents future clutter.
2. Do #7 next — removes the external snapshot safely.
3. Do #3 — classify transient root files.
4. Do #2 — failure taxonomy linter.
5. Do #1 — trace schema migration (largest, may span multiple sessions).
6. Do #5 — consolidate `state/` after trace/failure cleanup.
7. Do #6 — document the new branch strategy once the repo is tidy.

---

## Definition of Done

- [ ] All High-priority tasks completed.
- [ ] `retrace.py` reports 0 untraced project files.
- [ ] `git status` shows no unexpected untracked files.
- [ ] Cleanup recorded in a trace and in `phases/phase-3-progress.md`.
