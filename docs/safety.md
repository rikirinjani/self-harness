# Safety & Scoping

## Denylist

The following actions are never allowed without explicit human approval:

- Editing `~/.config/opencode/auth.json`, `.env`, `secrets/`, `credentials/`
- Pushing or merging without human approval
- Running `git push --force` or `git reset --hard` on shared branches
- Deleting files outside `self-harness/traces/` and `self-harness/failures/`
- Modifying `self-harness/constitution.md` (immutable per Article IV)
- Installing npm/pip packages globally without confirmation
- Executing `taskkill /F /IM` or `kill -9` on non-owned processes
- Any action that deletes or overwrites `opencode.db`

## Auto-merge Policy

- Never auto-merge PRs. PRs require human review and explicit approval.
- Sub-agent fixes in worktrees require human gate before merging to main.

## MCP Scopes

| MCP Server | Allowed for | Denied actions |
|-----------|-------------|---------------|
| pharmacy | oracle, librarian | `submit_order`, `stop_order` (read-only: search, info, dosage) |
| memory | all agents | None |
| vision | designer, fixer | None |
| google-workspace | general | None |
| agent-mesh | all agents | None |

## Tool Permissions per Agent Role

| Agent | Allowed tools | Denied tools |
|-------|-------------|-------------|
| oracle | read, grep, glob, webfetch, task | write, edit, bash (read-only) |
| librarian | read, grep, glob, webfetch, task | write, edit, bash |
| explorer | read, grep, glob, task | write, edit |
| fixer | read, grep, glob, write, edit, bash | task (delegation only), memory |
| designer | read, write, edit, bash, vision | task |
| general | all tools | none |

*Self-harness compliance is tracked in session traces and verified by the validate-skills tool.*
