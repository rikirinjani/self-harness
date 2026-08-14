#!/usr/bin/env python3
"""
crashlog.py -- Checkpoint recorder for session crash recovery.

Writes a lightweight state file during task execution. If the session
crashes, the next session reads the crash log and knows what was in flight.

Usage:
    # Record a checkpoint during a task
    python crashlog.py --checkpoint "Writing article body, paragraph 4" --files day11-article.md

    # Check for a crash log on session start
    python crashlog.py --recover

    # Clear the crash log after successful task completion
    python crashlog.py --clear
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CRASHLOG_FILE = Path("C:/Users/think/self-harness/crashlog.json")

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def write_checkpoint(description: str, files: list[str], task: str = ""):
    """Write a checkpoint to the crash log."""
    entry = {
        "status": "in_flight",
        "task": task,
        "last_checkpoint": description,
        "files_touched": files,
        "timestamp": now_iso(),
    }
    CRASHLOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CRASHLOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)
    print(f"  checkpoint: {description[:60]}")

def check_recovery() -> bool:
    """Check if a crash log exists from a previous session. Returns True if crash detected."""
    if not CRASHLOG_FILE.exists():
        print("  no crash log found — clean start")
        return False

    try:
        with open(CRASHLOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("  crash log corrupted — ignoring")
        CRASHLOG_FILE.unlink(missing_ok=True)
        return False

    status = data.get("status", "unknown")
    if status == "completed":
        print("  previous session completed cleanly")
        CRASHLOG_FILE.unlink(missing_ok=True)
        return False

    timestamp = data.get("timestamp", "unknown")
    task = data.get("task", "unknown")
    checkpoint = data.get("last_checkpoint", "unknown")
    files = data.get("files_touched", [])

    print()
    print("  ========================================")
    print("  CRASH DETECTED — previous session died")
    print(f"  When:      {timestamp}")
    print(f"  Task:      {task}")
    print(f"  Stopped at: {checkpoint}")
    print(f"  Dirty files: {', '.join(files) if files else '(none recorded)'}")
    print("  ========================================")
    print()
    print("  Recovery options:")
    print("    1. Resume     — pick up from the last checkpoint")
    print("    2. Retry      — restart the task from scratch")
    print("    3. Skip       — move on, leave the crash log for later")
    print()
    return True

def mark_completed():
    """Mark the crash log as completed — task finished successfully."""
    if CRASHLOG_FILE.exists():
        try:
            with open(CRASHLOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        data["status"] = "completed"
        data["completed_at"] = now_iso()
        with open(CRASHLOG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("  crash log: marked completed")

def clear():
    """Remove the crash log entirely."""
    if CRASHLOG_FILE.exists():
        CRASHLOG_FILE.unlink()
        print("  crash log: cleared")
    else:
        print("  no crash log to clear")

def main():
    parser = argparse.ArgumentParser(
        description="crashlog — checkpoint recorder for session crash recovery",
    )
    parser.add_argument(
        "--checkpoint", type=str,
        help="Record a checkpoint (e.g. 'Writing article, paragraph 4')",
    )
    parser.add_argument(
        "--files", nargs="*", default=[],
        help="Files currently being touched",
    )
    parser.add_argument(
        "--task", type=str, default="",
        help="Task description for the crash log header",
    )
    parser.add_argument(
        "--recover", action="store_true",
        help="Check for crash log from previous session",
    )
    parser.add_argument(
        "--complete", action="store_true",
        help="Mark crash log as completed (task finished successfully)",
    )
    parser.add_argument(
        "--clear", action="store_true",
        help="Remove the crash log entirely",
    )
    args = parser.parse_args()

    if args.checkpoint:
        write_checkpoint(args.checkpoint, args.files, args.task)
    elif args.recover:
        check_recovery()
    elif args.complete:
        mark_completed()
    elif args.clear:
        clear()
    else:
        # Default: show current state
        if CRASHLOG_FILE.exists():
            try:
                with open(CRASHLOG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                print(json.dumps(data, indent=2))
            except Exception:
                print("  crash log unreadable")
        else:
            print("  no crash log — clean state")

if __name__ == "__main__":
    main()
