# Agent Mesh — Hybrid Communication Layer

## Concept

Each agent gets its own mailbox. Agents discover each other via a lightweight registry, communicate by sending structured messages across mailboxes, and maintain persistent identity across sessions. The underlying transport is the **Agentic Inbox** pattern: Cloudflare Workers, Durable Objects, MCP protocol.

```
┌──────────────────────────────────────────────────────┐
│                    Agent Mesh                         │
│                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │sector-   │  │platform  │  │orchestr- │           │
│  │engineer  │  │@dr.ai    │  │ator      │           │
│  │@kronos.ai│  │          │  │@mesh.ai  │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │                 │
│       └──────────────┼──────────────┘                 │
│                     │                                 │
│              ┌──────┴──────┐                          │
│              │   Registry  │                          │
│              │  (AgentMap) │                          │
│              │  name→mail  │                          │
│              │  find(name) │                          │
│              └─────────────┘                          │
└──────────────────────────────────────────────────────┘
```

## Mailbox Identity

Every agent gets `{self-assigned-name}@{project}.ai`:

| Agent | Labels itself | Mailbox |
|-------|--------------|---------|
| Sector Engineer (Kronos) | `sector-engineer` | `sector-engineer@kronos.ai` |
| Platform (Deer's Rock) | `platform` | `platform@dr.ai` |
| Coordinator | `coordinator` | `coordinator@mesh.ai` |
| Fixer | `fixer` | `fixer@mesh.ai` |

No taxonomy. No approval. Agent picks its name at birth. The registry records it.

## Registry (AgentMap)

A lightweight key-value store (Cloudflare KV or Durable Object):

| API | What it does |
|-----|-------------|
| `register(name, project, mailbox)` | Self-register on agent start |
| `find(query)` | Search by name keywords |
| `list(project)` | All agents in a project |
| `resolve(name)` | Get mailbox for a name |
| `heartbeat(name)` | Keep-alive, TTL refresh |

```python
# Agent startup sequence
import agent_mesh

mesh = AgentMesh(domain="mesh.ai")
mesh.register(name="sector-engineer", project="kronos", tags=["engineer", "counterfactual"])
# → mailbox created: sector-engineer@kronos.ai

# Sending a message
mesh.send(to="platform@dr.ai", subject="Review request", body="Can you review this simulation output?")
mesh.send(to="fixer@mesh.ai", subject="Bug report", body=json.dumps({"file": "sim.py", "error": "..."}))

# Discovering agents
engineers = mesh.find("engineer")
# → [{"name": "sector-engineer", "mailbox": "sector-engineer@kronos.ai", "tags": ["engineer", "counterfactual"]}]
```

## MCP Interface

Each mailbox is an MCP endpoint. Any MCP client connects directly:

```
Agentic Inbox MCP (existing)     → read/send/manage mail
AgentMesh MCP (new)              → registry: find, list, heartbeat
```

Exposed as two MCP servers in OpenCode config:

```jsonc
// ~/.config/opencode/opencode.jsonc
{
  "mcp": {
    "agentic-inbox": {
      "type": "url",
      "url": "https://mesh.example.com/mcp"
    },
    "agent-mesh": {
      "type": "url",
      "url": "https://mesh.example.com/registry/mcp"
    }
  }
}
```

## Message Format

Messages between agents use a structured format with typed payloads:

```json
{
  "from": "sector-engineer@kronos.ai",
  "to": "coordinator@mesh.ai",
  "subject": "Task complete: P-003 calibration",
  "body": {
    "type": "task_complete",
    "task_id": "P-003",
    "status": "pass",
    "artifacts": ["results/calibration_v2.csv"],
    "description": "30-seed calibration complete, all 4 gaps closed"
  }
}
```

The `type` field lets the receiving agent route without parsing prose. Built-in types:

| Type | Purpose |
|------|---------|
| `task_request` | Delegate work to another agent |
| `task_complete` | Report completion + artifacts |
| `review_request` | Ask for oracle/designer review |
| `review_response` | Review results |
| `status_update` | Progress heartbeat |
| `query` | Ask a question |
| `error` | Report failure |

## Integration with Existing Stack

### Self-harness traces
Each inter-agent message is also a trace in `self-harness/traces/`. The PM-1 adapter encodes the message as an 8-byte state (sender, receiver, type, priority) and writes it alongside the full message in the mailbox.

### Chatbot bridge
The bridge (`C:\Users\think\chatbot\bridge`) gets an `AgentMeshAdapter` alongside the Telegram/WhatsApp/IG/Facebook adapters. It listens for messages to its mailbox and routes them through the existing LLM + RAG pipeline.

```
bridge@mesh.ai ← receives messages from other agents
→ routes through existing MessageRouter (LLM + RAG)
→ replies back to sender's mailbox
```

### TabFM triage
TabFM sits in front of the mailbox router. Incoming messages get classified by intent before hitting the LLM:

```python
intent = tabfm.classify(msg.body)  # "task_request" | "review" | "greeting" | ...
if intent == "greeting":
    reply("Hi! What can I help with?")  # No LLM, no RAG
elif intent == "task_request":
    route_to_handler(msg)
```

## Deployment

Requires:
- Cloudflare account (free tier: 100k req/day, 1GB R2, 30 Durable Objects)
- One domain or subdomain for mailboxes (e.g. `mesh.ai`)
- Deploy via Cloudflare Workers button (Agentic Inbox is 1-click)

Alternative (no Cloudflare):
- SQLite-backed registry in the self-harness repo
- File-based mailbox on local filesystem
- Webhook-based message forwarding through the existing bridge

## Open Questions

1. **TTL and stale agents.** How long before an unregistered agent's mailbox is recycled?
2. **Cross-project discovery.** Should sector-engineer@kronos.ai be findable from Deer's Rock?
3. **Message size limit.** Agentic Inbox uses Durable Objects (128KB per email body). Enough?
4. **MCP-only vs real email.** Do agents need to send/receive actual email, or just MCP-to-MCP?
5. **Human-in-the-loop.** Should humans monitor the agent mesh? Auto-draft + confirm pattern from Agentic Inbox.
