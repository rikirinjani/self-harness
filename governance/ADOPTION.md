# ADOPTION — GPT-6 Astra fix bundle (apply-astra-fixes, run 3907934)

**UPDATE 2026-10-02 (L3 governance adoption):** Rule 11 (required review and degraded
operation — deterministic risk classification, required-review contract, fail-stop
degraded-mode table, human-only exceptions) is **adopted and appended to
`~/.config/opencode/RULES.md`**; Rule 3 now points to `ROLE-MATRIX.md` (v1.0) as the
authoritative role/permission matrix with the delegation-contract requirement. Explicit
human authorization given via structured decision; independent verifier APPROVE
(103-line ordinal comparison, no contradictions). See QMS
`VER-L3-GOVERNANCE-ADOPTION-001`. Behavioral effect: delegation billing failure and
missing review now STOP work instead of permitting orchestrator takeover.

**UPDATE 2026-10-02 (L2 install):** the acceptance gate is now **installed and externally executed**.
`verify-change` (repo root) + CI workflow live on protected `main` of `rikirinjani/somnium-engine`
(commit `41df4b7`); operator config applied (repo variables `TYPECHECK_COMMAND=npm run check`,
`ACCEPTANCE_HUMAN_IDS`; environment `change-acceptance` with required reviewer +
`prevent_self_review` + `can_admins_bypass=false`; branch protection on `main` requiring the
`acceptance` check with `enforce_admins`, and on `acceptance-evidence` forbidding force-push/deletion).
Two PRs exercised the full chain: policy PASS + verify-exact-change PASS on both; approval PENDING
(fail-closed — requester cannot self-approve; needs a second human). The gate caught a real
autocrlf checksum bug in CI and rejects all 4 tamper variants (5/5 probes). `run-evidence.py`
was exercised end-to-end on Kaggle Linux producing a valid revision-bound record for `c7b0543`.
See QMS `VER-L2-GATE-INSTALL-001`.

Source: Kaggle task `rikirinjani/apply-astra-fixes` v1, model `gpt-6-astra`,
completed 2026-10-02 01:02:40Z (14m49s, 47,479 output tokens, $2.66).
Run result: `errors=0`, `total_chars=167615`. Local bundle copied verbatim from the
downloaded run artifacts into `self-harness/governance/`.

## Status per artifact

| Artifact | Adopted | Status / constraint |
|---|---|---|
| `acceptance-gate/verify-change` | yes | **Not yet wired.** Bash script; runs only under POSIX CI or Git Bash. Requires operator setup for protected branch + required check (stated inside the file). |
| `acceptance-gate/.github/workflows/verify-change.yml` | yes (as template) | **Not installed in any repo.** Installing into `Somnium Engine/.github/workflows/` requires an L2 worktree change + human approval + push. Until then the gate is advisory only. |
| `evidence-binding/run-evidence.py` | yes | POSIX-only (`fcntl`); cannot run on native Windows — needs CI/WSL. Unexecuted locally. |
| `evidence-binding/EVIDENCE-SCHEMA.md` | yes (composite) | **Gap:** gpt-6-astra omitted this file. Sections 1–2 from `gemini-3.7-flash` (truncated draft), Section 3 completed locally against `run-evidence.py`'s actual record writer. |
| `degraded-modes/RULES-degraded-ops.md` | yes (draft) | Adds proposed `Rule 11` to RULES.md. **Not yet appended to `~/.config/opencode/RULES.md`** — requires explicit human adoption (it changes acceptance rules). |
| `role-matrix-contracts/ROLE-MATRIX.md` | yes (draft) | Self-declaring: replaces RULES.md Rule 3 only "on explicit human adoption". **Not adopted.** |
| `role-matrix-contracts/delegation-contract-template.md` | yes (draft) | Effective only alongside ROLE-MATRIX adoption. |
| `control-tests/test_controls.py` | yes | Self-contained (temp git repos, no pytest needed). **Run locally: see verification below.** Ships its own reference gate; explicitly does NOT certify the real `retrace.py`/`crashlog.py` (documented assurance boundary inside the file). |
| `overhead-metrics/measure_overhead.py` + `metrics.md` | yes | Measurement harness only; requires baseline runs to produce numbers. No data collected yet. |

## Verification performed (local)

- `python control-tests/test_controls.py` — result recorded in the session trace
  (`self-harness/traces/`) and reported in the re-review hand-off.

## Honest boundary

Adopting a file here means "stored in the governance bundle and available". It does **not**
mean enforced. The three externally-enforced controls Astra demanded (protected CI gate,
machine-observed evidence wired into merge, fault-injection suite running in CI) remain
**pending operator setup**; the rest are pending explicit human adoption where the
documents themselves require it.
