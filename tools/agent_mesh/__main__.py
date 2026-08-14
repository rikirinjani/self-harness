"""pm1-mesh CLI — agent registration and messaging."""

import argparse
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from agent_mesh.registry import AgentRegistry, Mailbox


def cmd_register(args):
    reg = AgentRegistry()
    result = reg.register(args.name, args.project, args.tags, args.account)
    print(f"Registered: {result['name']} -> {result['mailbox']}")
    print(f"  Project: {result['project']}")
    print(f"  ID: {result['agent_id']}")


def cmd_find(args):
    reg = AgentRegistry()
    results = reg.find(args.query)
    if not results:
        print("No agents found.")
        return
    for r in results:
        tags = json.loads(r.get("tags", "[]"))
        print(f"  {r['mailbox']}  ({r['project']})  [{', '.join(tags)}]")


def cmd_list(args):
    reg = AgentRegistry()
    if args.project:
        results = reg.list_project(args.project)
    else:
        results = reg.list_all()
    if not results:
        print("No agents registered.")
        return
    for r in results:
        tags = json.loads(r.get("tags", "[]"))
        hb = r.get("last_heartbeat", "")[:16] if r.get("last_heartbeat") else "-"
        print(f"  {r['mailbox']:40s} {r['project']:15s} {hb}")


def cmd_send(args):
    reg = AgentRegistry()
    mb = Mailbox(reg)
    result = mb.send(args.from_mailbox, args.to, args.subject, args.body, args.type)
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    for t in result["targets"]:
        print(f"  -> {t['to']} (id: {t['message_id'][:8]}...)")


def cmd_read(args):
    reg = AgentRegistry()
    mb = Mailbox(reg)
    messages = mb.read(args.mailbox, args.limit, args.status)
    if not messages:
        print(f"No messages ({args.status or 'all'}).")
        return
    for m in messages:
        status = "📬" if m["status"] == "unread" else "📖"
        created = m["created_at"][:19] if m["created_at"] else ""
        print(f"  {status} [{created}] {m['from_mailbox']} -> {m['to_mailbox']}")
        print(f"     Subject: {m['subject']}")
        print(f"     Type: {m['msg_type']}")
        print()


def cmd_count(args):
    reg = AgentRegistry()
    mb = Mailbox(reg)
    unread = mb.count(args.mailbox, "unread")
    total = mb.count(args.mailbox, None)
    print(f"  {args.mailbox}: {unread} unread / {total} total")


def cmd_heartbeat(args):
    reg = AgentRegistry()
    ok = reg.heartbeat(args.mailbox)
    if ok:
        print(f"  {args.mailbox}: heartbeat OK")
    else:
        print(f"  {args.mailbox}: not found")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Agent Mesh CLI")
    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("register", help="Register an agent")
    sp.add_argument("--name", required=True)
    sp.add_argument("--project", default="mesh")
    sp.add_argument("--tags", nargs="*", default=[])
    sp.add_argument("--account", default="")

    sp = sub.add_parser("find", help="Search agents")
    sp.add_argument("query")

    sp = sub.add_parser("list", help="List agents")
    sp.add_argument("--project", default="")

    sp = sub.add_parser("send", help="Send a message")
    sp.add_argument("--from", dest="from_mailbox", required=True)
    sp.add_argument("--to", required=True)
    sp.add_argument("--subject", default="")
    sp.add_argument("--body", default="")
    sp.add_argument("--type", default="message")

    sp = sub.add_parser("read", help="Read mailbox")
    sp.add_argument("mailbox")
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--status", default="", choices=["", "unread", "read", "archived"])

    sp = sub.add_parser("count", help="Count messages")
    sp.add_argument("mailbox")

    sp = sub.add_parser("heartbeat", help="Send heartbeat")
    sp.add_argument("mailbox")

    args = parser.parse_args()
    if args.command == "register":
        cmd_register(args)
    elif args.command == "find":
        cmd_find(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "send":
        cmd_send(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "count":
        cmd_count(args)
    elif args.command == "heartbeat":
        cmd_heartbeat(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
