"""Retrace scanner — find untraced work and prompt for retroactive traces.

Usage:
    python tools/retrace.py                          # Full scan
    python tools/retrace.py --quick                  # Quick scan (recent only)
    python tools/retrace.py --agent <name>            # Scan for specific agent
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TRACES_DIR = Path.home() / "self-harness" / "traces"
KNOWN_PROJECTS = {
    "chatbot/whatsapp-sidecar": "whatsmeow Go sidecar",
    "chatbot/bridge": "Multi-channel chatbot bridge",
    "chatbot/hf-parser-space": "HF Space parser",
    "morse": "PM-1 protocol",
    "morse/opencode_plugin": "PM-1 OpenCode integration",
    "morse/paper": "PM-1 paper draft",
    "self-harness/tools": "Self-harness tools (validator, mesh, webmail, workspace)",
    "self-harness/docs": "Self-harness docs",
    "self-harness/patterns": "Skill registry",
    "self-harness/.github": "CI templates",
}

CHECKED = set()


def get_all_trace_slugs() -> set[str]:
    """Get all slugs that have been traced."""
    slugs = set()
    for f in TRACES_DIR.glob("*.pm1"):
        try:
            d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
            s = d.get("session_id", "") or d.get("metadata", {}).get("slug", "")
            if s:
                slugs.add(s)
        except (json.JSONDecodeError, OSError):
            continue
    for f in TRACES_DIR.glob("*.json"):
        try:
            d = json.loads(f.read_text(encoding="utf-8-sig", errors="replace"))
            s = d.get("slug", "") or d.get("trace_id", "") or d.get("session_id", "")
            if s:
                slugs.add(s)
        except (json.JSONDecodeError, OSError):
            continue
    return slugs


def check_project(project_path: str, description: str, slugs: set[str]) -> list[dict]:
    """Check if a project has any trace coverage."""
    base = Path.home() / project_path
    if not base.exists():
        return []

    findings = []
    keywords = project_path.replace("/", "-").replace("\\", "-").split("-")

    # Check if any trace covers this project
    covered = False
    for slug in slugs:
        slug_lower = slug.lower()
        if any(kw.lower() in slug_lower for kw in keywords if len(kw) > 2):
            covered = True
            break

    if not covered:
        findings.append({
            "project": project_path,
            "description": description,
            "status": "untraced",
            "suggestion": f"pm1-trace trace --agent <agent> --outcome pass --action \"Work on {description}\" --slug {project_path.replace('/', '-')}",
        })

    return findings


def scan_recent_agents() -> list[str]:
    """Scan the agent mesh for registered agents with no traces."""
    try:
        result = subprocess.run(
            ["pm1-mesh", "list"],
            capture_output=True, text=True, timeout=10,
        )
        agents = []
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if parts and "@" in parts[0]:
                agents.append(parts[0])
        return agents
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def scan_unmatched_agents(slugs: set[str]) -> list[dict]:
    """Check if any mesh agents lack trace coverage."""
    findings = []
    agents = scan_recent_agents()
    for mailbox in agents:
        name = mailbox.split("@")[0]
        if name not in slugs and name != "general":
            findings.append({
                "project": f"mesh:{mailbox}",
                "description": f"Agent {mailbox} has no trace",
                "status": "untraced",
                "suggestion": f"pm1-trace trace --agent {name} --outcome pass --action \"Agent {mailbox} work\"",
            })
    return findings


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Find untraced work and prompt for retraces")
    parser.add_argument("--quick", action="store_true", help="Quick scan (known projects only)")
    parser.add_argument("--agent", default="", help="Filter by agent name")
    args = parser.parse_args()

    print("Retrace Scanner\n")
    existing_slugs = get_all_trace_slugs()
    print(f"Existing traces: {len(existing_slugs)}\n")

    findings = []

    # Check known projects
    for path, desc in KNOWN_PROJECTS.items():
        findings.extend(check_project(path, desc, existing_slugs))

    # Check mesh agents
    if not args.quick:
        findings.extend(scan_unmatched_agents(existing_slugs))

    # Filter by agent if specified
    if args.agent:
        findings = [f for f in findings if args.agent.lower() in f["project"].lower() or args.agent.lower() in f["description"].lower()]

    if not findings:
        print("  No untraced work found. All projects have trace coverage.")
        return 0

    print(f"  Found {len(findings)} untraced item(s):\n")
    for f in findings:
        print(f"  [{f['project']}]")
        print(f"    {f['description']}")
        print(f"    Status: {f['status']}")
        print(f"    Fix: {f['suggestion']}")
        print()

    print("  To write retraces, run the suggested pm1-trace commands above.")
    print("  RULES.md Rule 7: Untraced work must be retraced before session close.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
