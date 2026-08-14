"""Agent Mesh MCP Server — exposes registry + mailbox tools over MCP stdio protocol.

OpenCode launches this as a subprocess MCP server.

Add to opencode.jsonc:
  "mcp": {
    "agent-mesh": {
      "type": "local",
      "command": ["python", "-u", "C:\\Users\\think\\self-harness\\tools\\mesh_mcp_server.py"]
    }
  }
"""

import json
import sys
import traceback

sys.path.insert(0, r"C:\Users\think\self-harness\tools")
from agent_mesh.registry import AgentRegistry, Mailbox

reg = AgentRegistry()
mb = Mailbox(reg)


def handle_request(req: dict) -> dict:
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {}) or {}

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": req_id, "result": {
            "protocolVersion": "0.1.0",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "agent-mesh", "version": "1.0.0"},
        }}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {
            "tools": [
                {
                    "name": "register_agent",
                    "description": "Register an agent in the mesh",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Agent name (self-assigned)"},
                            "project": {"type": "string", "description": "Project name"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Search tags"},
                        },
                        "required": ["name"],
                    },
                },
                {
                    "name": "find_agents",
                    "description": "Search for agents by name, project, or tags",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "list_agents",
                    "description": "List all agents, optionally filtered by project",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "Filter by project"},
                        },
                    },
                },
                {
                    "name": "send_message",
                    "description": "Send a message to an agent, project, or broadcast",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string", "description": "Sender's mailbox"},
                            "to": {"type": "string", "description": "Recipient mailbox (agent@project.ai, project@mesh.ai, broadcast@mesh.ai)"},
                            "subject": {"type": "string"},
                            "body": {"type": "string", "description": "Message body or JSON payload"},
                            "type": {"type": "string", "description": "Message type (message, task_request, task_complete, review_request, query, error)"},
                        },
                        "required": ["from", "to"],
                    },
                },
                {
                    "name": "read_mailbox",
                    "description": "Read messages in a mailbox",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "mailbox": {"type": "string", "description": "Mailbox to read"},
                            "limit": {"type": "number", "default": 20},
                            "status": {"type": "string", "enum": ["", "unread", "read"]},
                        },
                        "required": ["mailbox"],
                    },
                },
                {
                    "name": "mark_read",
                    "description": "Mark a message as read",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string"},
                        },
                        "required": ["message_id"],
                    },
                },
                {
                    "name": "mailbox_count",
                    "description": "Count unread and total messages in a mailbox",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "mailbox": {"type": "string"},
                        },
                        "required": ["mailbox"],
                    },
                },
                {
                    "name": "heartbeat",
                    "description": "Send agent heartbeat (keeps registration alive)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "mailbox": {"type": "string"},
                        },
                        "required": ["mailbox"],
                    },
                },
            ],
        }}

    if method == "tools/call":
        tool = params.get("name", "")
        args = params.get("arguments", {}) or {}

        try:
            if tool == "register_agent":
                result = reg.register(args.get("name", "?"), args.get("project", "mesh"), args.get("tags"))
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}

            elif tool == "find_agents":
                result = reg.find(args.get("query", ""))
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}

            elif tool == "list_agents":
                if args.get("project"):
                    result = reg.list_project(args["project"])
                else:
                    result = reg.list_all()
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}

            elif tool == "send_message":
                result = mb.send(args["from"], args["to"], args.get("subject", ""),
                                 args.get("body", ""), args.get("type", "message"))
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}

            elif tool == "read_mailbox":
                result = mb.read(args["mailbox"], int(args.get("limit", 20)), args.get("status") or None)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}}

            elif tool == "mark_read":
                ok = mb.mark_read(args["message_id"])
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"ok": ok})}]}}

            elif tool == "mailbox_count":
                unread = mb.count(args["mailbox"], "unread")
                total = mb.count(args["mailbox"], None)
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"unread": unread, "total": total})}]}}

            elif tool == "heartbeat":
                ok = reg.heartbeat(args["mailbox"])
                return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"ok": ok})}]}}

            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool}"}}

        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """Read JSON-RPC requests from stdin, write responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
        except json.JSONDecodeError:
            resp = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
