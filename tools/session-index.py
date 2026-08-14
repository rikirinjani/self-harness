#!/usr/bin/env python3
"""
session-index.py — Append-only session journal.

Captures the session-level picture that individual traces miss.
Written at session end. Read at session start.

Usage:
    # Close this session and append to the index
    python session-index.py --close \\
        --goal "Write and publish Day 12" \\
        --key-decisions "The philosophical zombie framing resonates" \\
        --open-questions "Does the reader want more architectural or more experiential content?" \\
        --files-created articles/day12-article.md scripts/publish-day12.mjs

    # Show the index on session start
    python session-index.py --recent 3
    python session-index.py --query "retrace"   # search by keyword
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INDEX_FILE = Path("C:/Users/think/self-harness/session-index.json")
TRACES_DIR = Path("C:/Users/think/self-harness/traces")
PROJECT_ROOT = Path("C:/Users/think/Project")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def load_index():
    if INDEX_FILE.exists():
        try:
            with open(INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"sessions": []}
    return {"sessions": []}

def save_index(data):
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_recent_traces(minutes=90):
    """Find traces from the last N minutes — assumed to be this session."""
    now = datetime.now(timezone.utc).timestamp()
    recent = []
    if not TRACES_DIR.exists():
        return recent
    files = sorted(TRACES_DIR.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
    for p in files:
        try:
            mt = p.stat().st_mtime
            if now - mt > minutes * 60:
                break  # files are newest-first, so once we hit old ones, stop
            with open(p, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            recent.append({
                "trace": p.stem,
                "action": data.get("action", "")[:120],
                "key_files": data.get("key_files", []),
                "agent": data.get("agent", ""),
                "outcome": data.get("outcome", ""),
            })
        except Exception:
            continue
    return recent

def close_session(goal, key_decisions, open_questions, files_created):
    index = load_index()
    traces = get_recent_traces()

    # Generic pass/fail counts from traces
    pass_count = sum(1 for t in traces if t.get("outcome") == "pass")
    fail_count = sum(1 for t in traces if t.get("outcome") == "fail")
    partial_count = sum(1 for t in traces if t.get("outcome") not in ("pass", "fail"))

    entry = {
        "session_id": f"session-{len(index['sessions']) + 1}",
        "timestamp": now_iso(),
        "goal": goal,
        "traces_this_session": len(traces),
        "traces": traces[:10],
        "trace_outcomes": {"pass": pass_count, "fail": fail_count, "other": partial_count},
        "key_decisions": key_decisions.split(";") if key_decisions else [],
        "open_questions": open_questions.split(";") if open_questions else [],
        "files_created": files_created,
    }

    index["sessions"].append(entry)
    save_index(index)

    print(f"  session index: session #{len(index['sessions'])} written")
    print(f"  traces captured: {len(traces)} ({pass_count} pass, {fail_count} fail, {partial_count} other)")
    if key_decisions:
        for d in entry["key_decisions"]:
            print(f"  decision: {d.strip()}")
    if open_questions:
        for q in entry["open_questions"]:
            print(f"  question: {q.strip()}")

def show_recent(n=3):
    index = load_index()
    sessions = index.get("sessions", [])
    if not sessions:
        print("  no sessions in index yet")
        return
    for s in sessions[-n:]:
        ts = s.get("timestamp", "?")[:19]
        goal = s.get("goal", "?")[:80]
        n_traces = s.get("traces_this_session", 0)
        kd = s.get("key_decisions", [])
        oq = s.get("open_questions", [])
        print(f"  [{ts}] {goal}")
        print(f"         {n_traces} traces, {len(kd)} decisions, {len(oq)} questions")
        if kd:
            for d in kd:
                print(f"         \u2192 {d.strip()}")
        print()

def query_index(keyword):
    index = load_index()
    sessions = index.get("sessions", [])
    results = []
    for s in sessions:
        text = json.dumps(s).lower()
        if keyword.lower() in text:
            results.append(s)
    if not results:
        print(f"  no sessions matching '{keyword}'")
        return
    print(f"  {len(results)} session(s) matching '{keyword}':")
    for s in results:
        ts = s.get("timestamp", "?")[:19]
        goal = s.get("goal", "?")[:80]
        print(f"    [{ts}] {goal}")

def main():
    parser = argparse.ArgumentParser(
        description="session-index — append-only session journal",
    )
    parser.add_argument("--close", action="store_true", help="Close current session and append to index")
    parser.add_argument("--goal", type=str, default="", help="Session goal description")
    parser.add_argument("--key-decisions", type=str, default="", help="Semicolon-separated key decisions")
    parser.add_argument("--open-questions", type=str, default="", help="Semicolon-separated open questions")
    parser.add_argument("--files-created", nargs="*", default=[], help="Files created this session")
    parser.add_argument("--recent", type=int, nargs="?", const=3, default=0, help="Show recent N sessions")
    parser.add_argument("--query", type=str, default="", help="Search sessions by keyword")
    args = parser.parse_args()

    if args.close:
        close_session(args.goal, args.key_decisions, args.open_questions, args.files_created)
    elif args.recent:
        show_recent(args.recent)
    elif args.query:
        query_index(args.query)
    else:
        # Default: show last session
        show_recent(1)

if __name__ == "__main__":
    main()
