"""Agent Registry — maps names to mailboxes, supports discovery."""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

MESH_DIR = Path.home() / ".agent-mesh"
REGISTRY_DB = MESH_DIR / "registry.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    project TEXT NOT NULL DEFAULT 'mesh',
    mailbox TEXT NOT NULL UNIQUE,
    tags TEXT DEFAULT '[]',
    last_heartbeat TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    from_mailbox TEXT NOT NULL,
    to_mailbox TEXT NOT NULL,
    subject TEXT DEFAULT '',
    body TEXT DEFAULT '',
    msg_type TEXT DEFAULT 'message',
    status TEXT DEFAULT 'unread',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_mailbox, status);
CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_mailbox);
CREATE INDEX IF NOT EXISTS idx_agents_project ON agents(project);
"""


def _get_db():
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(REGISTRY_DB))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


class AgentRegistry:
    """Registry for agent discovery and mailbox routing."""

    def __init__(self):
        self.conn = _get_db()

    def register(self, name: str, project: str = "mesh",
                  tags: list[str] | None = None, account: str | None = None) -> dict:
        """Register an agent. Returns its mailbox."""
        agent_id = uuid.uuid4().hex[:12]
        domain = account or "mesh.ai"
        mailbox = f"{name}@{project}.{domain}" if project and project != "mesh" else f"{name}@{domain}"
        tags_json = json.dumps(tags or [])
        now = datetime.now(timezone.utc).isoformat()

        self.conn.execute(
            "INSERT OR REPLACE INTO agents (id, name, project, mailbox, tags, last_heartbeat) VALUES (?, ?, ?, ?, ?, ?)",
            (agent_id, name, project, mailbox, tags_json, now),
        )
        self.conn.commit()

        return {"agent_id": agent_id, "name": name, "project": project,
                "mailbox": mailbox, "tags": tags or []}

    def find(self, query: str) -> list[dict]:
        """Search agents by name, project, or tags."""
        q = f"%{query}%"
        rows = self.conn.execute(
            "SELECT DISTINCT a.* FROM agents a WHERE a.name LIKE ? OR a.project LIKE ? OR a.tags LIKE ?",
            (q, q, q),
        ).fetchall()
        return [dict(r) for r in rows]

    def list_project(self, project: str) -> list[dict]:
        """List all agents in a project."""
        rows = self.conn.execute(
            "SELECT * FROM agents WHERE project = ?", (project,)
        ).fetchall()
        return [dict(r) for r in rows]

    def list_all(self) -> list[dict]:
        """List all registered agents."""
        rows = self.conn.execute("SELECT * FROM agents ORDER BY created_at").fetchall()
        return [dict(r) for r in rows]

    def resolve(self, mailbox: str) -> list[str]:
        """Resolve a mailbox to one or more delivery targets.

        agent@project.ai → single agent
        project@mesh.ai → all agents in that project
        account@mesh.ai → all agents
        """
        parts = mailbox.split("@")
        if len(parts) != 2:
            return []
        local, domain = parts

        # Account-wide broadcast: account@mesh.ai
        if local == "broadcast" and domain == "mesh.ai":
            rows = self.conn.execute("SELECT mailbox FROM agents").fetchall()
            return [r["mailbox"] for r in rows]

        # Project-wide broadcast: project@mesh.ai
        if domain == "mesh.ai":
            rows = self.conn.execute("SELECT mailbox FROM agents WHERE project = ?", (local,)).fetchall()
            if rows:
                return [r["mailbox"] for r in rows]

        # Direct agent mailbox
        row = self.conn.execute("SELECT mailbox FROM agents WHERE mailbox = ?", (mailbox,)).fetchone()
        if row:
            return [row["mailbox"]]

        return []

    def heartbeat(self, mailbox: str) -> bool:
        """Update agent heartbeat."""
        now = datetime.now(timezone.utc).isoformat()
        cur = self.conn.execute(
            "UPDATE agents SET last_heartbeat = ? WHERE mailbox = ?", (now, mailbox)
        )
        self.conn.commit()
        return cur.rowcount > 0


class Mailbox:
    """Per-mailbox message storage."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def send(self, from_mailbox: str, to_mailbox: str,
             subject: str = "", body: str = "", msg_type: str = "message") -> dict:
        """Send a message. Returns targets delivered to."""
        targets = self.registry.resolve(to_mailbox)
        if not targets:
            return {"error": f"Unknown mailbox: {to_mailbox}", "targets": []}

        delivered = []
        for target in targets:
            msg_id = uuid.uuid4().hex[:16]
            self.registry.conn.execute(
                "INSERT INTO messages (id, from_mailbox, to_mailbox, subject, body, msg_type) VALUES (?, ?, ?, ?, ?, ?)",
                (msg_id, from_mailbox, target, subject, body, msg_type),
            )
            delivered.append({"message_id": msg_id, "to": target})
        self.registry.conn.commit()

        return {"status": "sent", "targets": delivered}

    def read(self, mailbox: str, limit: int = 20, status: str | None = None) -> list[dict]:
        """Read messages from a mailbox."""
        if status:
            rows = self.registry.conn.execute(
                "SELECT * FROM messages WHERE to_mailbox = ? AND status = ? ORDER BY created_at DESC LIMIT ?",
                (mailbox, status, limit),
            ).fetchall()
        else:
            rows = self.registry.conn.execute(
                "SELECT * FROM messages WHERE to_mailbox = ? ORDER BY created_at DESC LIMIT ?",
                (mailbox, limit),
            ).fetchall()
        return [dict(r) for r in rows]

    def mark_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        cur = self.registry.conn.execute(
            "UPDATE messages SET status = 'read' WHERE id = ?", (message_id,)
        )
        self.registry.conn.commit()
        return cur.rowcount > 0

    def count(self, mailbox: str, status: str = "unread") -> int:
        """Count messages in a mailbox."""
        row = self.registry.conn.execute(
            "SELECT COUNT(*) as c FROM messages WHERE to_mailbox = ? AND status = ?",
            (mailbox, status),
        ).fetchone()
        return row["c"] if row else 0
