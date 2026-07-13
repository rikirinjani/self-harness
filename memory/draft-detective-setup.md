# Draft Detective — Session Memory

## What
AI-powered peer review tool (draft-detective) installed at C:\Users\think\Peer Review\draft-detective

## MCP Config
Registered in opencode.jsonc as "draft-detective" — runs via standalone_mcp.py

## Bugs Fixed
1. lib/skills.py: ead_text() missing encoding="utf-8" — crashed on Windows with curly quotes in SKILL.md
2. lib/config/rate_limiter.py: Postgres required even in standalone mode — added STANDALONE_MODE env var ? InMemoryRateLimiter
3. standalone_mcp.py: ull_review passed document_text but agent expects document_markdown
4. standalone_mcp.py: missing os.environ.setdefault("STANDALONE_MODE", "1") at startup

## Limitations
- MCP tools (via standalone_mcp.py) don't work with DeepSeek API — structured output (/v1/chat/completions with response_format) and deepagents (Responses API) unsupported
- Direct API calls to opencode-go work for ad-hoc reviews
- Requires OpenAI-compatible provider with structured output support for full MCP tool functionality

## Peer Review Performed
- Paper: Deers-Rock submission (healthcare simulation platform)
- Used direct API call to opencode-go deepseek-v4-flash
- Result: Major Revisions — 5 major issues identified
