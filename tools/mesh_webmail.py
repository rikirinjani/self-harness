"""Agent Mesh Webmail — browse agent messages in your browser.

Run: python self-harness/tools/mesh_webmail.py
Open: http://localhost:9090
"""

import http.server
import json
import sqlite3
import urllib.parse
from pathlib import Path

MESH_DIR = Path.home() / ".agent-mesh"
REGISTRY_DB = MESH_DIR / "registry.db"
PORT = 9090


def get_data():
    conn = sqlite3.connect(str(REGISTRY_DB))
    conn.row_factory = sqlite3.Row

    agents = conn.execute("SELECT * FROM agents ORDER BY created_at").fetchall()
    messages = conn.execute("""
        SELECT m.*, a.project as sender_project
        FROM messages m
        LEFT JOIN agents a ON a.mailbox = m.from_mailbox
        ORDER BY m.created_at DESC LIMIT 100
    """).fetchall()
    conn.close()
    return agents, messages


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent Mesh Inbox</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #222; }}
.header {{ background: #1a1a2e; color: #fff; padding: 16px 24px; display: flex; align-items: center; gap: 12px; }}
.header h1 {{ font-size: 20px; font-weight: 600; }}
.header .badge {{ background: #e94560; color: #fff; padding: 2px 10px; border-radius: 12px; font-size: 13px; }}
.layout {{ display: flex; height: calc(100vh - 56px); }}
.sidebar {{ width: 260px; background: #fff; border-right: 1px solid #e0e0e0; padding: 16px; overflow-y: auto; }}
.sidebar h3 {{ font-size: 11px; text-transform: uppercase; color: #888; margin: 16px 0 8px; letter-spacing: 1px; }}
.agent {{ display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-radius: 6px; font-size: 13px; cursor: default; }}
.agent:hover {{ background: #f0f0f5; }}
.agent .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #4ade80; flex-shrink: 0; }}
.agent .name {{ font-weight: 500; }}
.agent .project {{ color: #888; font-size: 11px; }}
.main {{ flex: 1; overflow-y: auto; padding: 16px 24px; }}
.msg {{ background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
.msg:hover {{ border-color: #1a1a2e; }}
.msg .meta {{ display: flex; justify-content: space-between; font-size: 12px; color: #888; margin-bottom: 6px; }}
.msg .from {{ font-weight: 600; color: #1a1a2e; font-size: 13px; }}
.msg .subject {{ font-weight: 500; font-size: 14px; margin: 4px 0; }}
.msg .body {{ font-size: 13px; color: #555; white-space: pre-wrap; margin-top: 6px; padding: 8px; background: #fafafa; border-radius: 4px; }}
.msg .type {{ display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px; background: #e8f4f8; color: #0284c7; }}
.empty {{ text-align: center; padding: 60px; color: #888; }}
.empty .big {{ font-size: 48px; margin-bottom: 12px; }}
</style>
</head>
<body>
<div class="header">
  <h1>Agent Mesh Inbox</h1>
  <span class="badge">{msg_count} messages</span>
  <span class="badge" style="background:#4ade80;color:#1a1a2e">{agent_count} agents</span>
</div>
<div class="layout">
  <div class="sidebar">
    <h3>Agents</h3>
    {agent_list}
  </div>
  <div class="main">
    {message_list}
  </div>
</div>
</body>
</html>"""


def render():
    agents, messages = get_data()

    agent_rows = []
    for a in agents:
        hb = (a["last_heartbeat"] or "")[:16] if a["last_heartbeat"] else "-"
        tags = json.loads(a["tags"] or "[]")
        tag_str = f"<span style='color:#888;font-size:11px'>[{', '.join(tags)}]</span>" if tags else ""
        agent_rows.append(
            f'<div class="agent">'
            f'<span class="dot"></span>'
            f'<div><div class="name">{a["name"]}</div>'
            f'<div class="project">{a["project"]} | {a["mailbox"]}</div>'
            f'{tag_str}</div></div>'
        )

    msg_rows = []
    for m in messages:
        created = (m["created_at"] or "")[:19] if m["created_at"] else ""
        body = m["body"] or ""
        body_short = body[:200] + ("..." if len(body) > 200 else "")
        status = "📬" if m["status"] == "unread" else "📖"
        msg_type = m["msg_type"]
        msg_rows.append(
            f'<div class="msg">'
            f'<div class="meta">'
            f'<span>{status} <span class="from">{m["from_mailbox"]}</span> -&gt; {m["to_mailbox"]}</span>'
            f'<span>{created}</span>'
            f'</div>'
            f'<span class="type">{msg_type}</span>'
            f'<div class="subject">{m["subject"] or "(no subject)"}</div>'
            f'<div class="body">{body_short}</div>'
            f'</div>'
        )

    return PAGE.format(
        msg_count=len(messages), agent_count=len(agents),
        agent_list="".join(agent_rows) if agent_rows else "<div style='color:#888;font-size:13px'>No agents</div>",
        message_list="".join(msg_rows) if msg_rows else
        "<div class='empty'><div class='big'>📭</div>No messages yet. Agents haven't started talking.</div>",
    )


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        html = render()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, fmt, *args):
        pass  # quiet


if __name__ == "__main__":
    print(f"  Agent Mesh Webmail: http://localhost:{PORT}")
    print(f"  Refresh to see new messages. Ctrl+C to stop.")
    httpd = http.server.HTTPServer(("", PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
