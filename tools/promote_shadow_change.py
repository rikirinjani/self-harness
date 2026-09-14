#!/usr/bin/env python3
"""Promote Shadow Change — Phase 6

Reads a shadow report and, on explicit human approval, copies the shadow files
into the active harness. Creates a snapshot before promotion for rollback.

Usage:
    python tools/promote_shadow_change.py shadow/reports/P-004-shadow-report.json
    python tools/promote_shadow_change.py P-004 --approve
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SHADOW_DIR = ROOT / "shadow"
SHADOW_REPORTS = SHADOW_DIR / "reports"
SHADOW_SNAPSHOTS = SHADOW_DIR / "snapshots"
ACTIVE_RULES = ROOT / "rules"
CHANGELOG = SHADOW_DIR / "CHANGELOG.md"


def load_report(path):
    if not path.exists():
        print(f"Shadow report not found: {path}")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def find_report(identifier):
    """Resolve P-NNN id or full path to a shadow report."""
    if Path(identifier).exists():
        return Path(identifier)
    candidate = SHADOW_REPORTS / f"{identifier}-shadow-report.json"
    if candidate.exists():
        return candidate
    print(f"Could not find shadow report for {identifier}")
    sys.exit(1)


def create_snapshot(proposal_id):
    """Snapshot active rules before promotion."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    snapshot_dir = SHADOW_SNAPSHOTS / f"{proposal_id}-{timestamp}"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    if ACTIVE_RULES.exists():
        shutil.copytree(ACTIVE_RULES, snapshot_dir / "rules", dirs_exist_ok=True)
    print(f"Snapshot created: {snapshot_dir}")
    return snapshot_dir


def copy_shadow_to_active(proposal_id):
    """Copy shadow rules to active rules."""
    shadow_rules = SHADOW_DIR / "rules"
    if not shadow_rules.exists():
        print("No shadow rules to promote.")
        sys.exit(1)
    ACTIVE_RULES.mkdir(parents=True, exist_ok=True)
    for src in shadow_rules.rglob("*"):
        if src.is_file():
            rel = src.relative_to(shadow_rules)
            dst = ACTIVE_RULES / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  promoted: {rel}")


def write_awaiting_approval(report_path, report):
    """Create an awaiting-approval record (veto window)."""
    await_path = SHADOW_REPORTS / f"{report['proposal_id']}-awaiting-approval.json"
    record = {
        "proposal_id": report["proposal_id"],
        "shadow_report": str(report_path),
        "status": "awaiting_human_approval",
        "created": datetime.now(timezone.utc).isoformat() + "Z",
        "instruction": "Run promote_shadow_change.py with --approve to deploy, or delete this file to veto."
    }
    await_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"Veto window opened: {await_path}")


def log_change(proposal_id, action, details=""):
    """Append to shadow changelog."""
    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {datetime.now(timezone.utc).isoformat()}Z | {action} | {proposal_id} | {details}\n"
    if CHANGELOG.exists():
        CHANGELOG.write_text(CHANGELOG.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        CHANGELOG.write_text(f"# Shadow Harness Changelog\n\n{line}", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Promote a shadow-approved harness change")
    parser.add_argument("report", help="Shadow report path or P-NNN id")
    parser.add_argument("--approve", action="store_true", help="Human approval to promote")
    args = parser.parse_args()

    report_path = find_report(args.report)
    report = load_report(report_path)
    proposal_id = report["proposal_id"]
    recommendation = report.get("recommendation", "manual_review")

    if recommendation != "deploy":
        print(f"Promotion blocked: shadow recommendation is '{recommendation}', not 'deploy'.")
        print(f"Review the report at {report_path}")
        sys.exit(1)

    if not args.approve:
        write_awaiting_approval(report_path, report)
        log_change(proposal_id, "awaiting_approval", f"veto window opened for {report_path}")
        print(f"\nPromotion of {proposal_id} is awaiting human approval.")
        print(f"To approve and promote, run:")
        print(f"  python tools/promote_shadow_change.py {proposal_id} --approve")
        print(f"To veto, delete: {SHADOW_REPORTS / f'{proposal_id}-awaiting-approval.json'}")
        sys.exit(0)

    snapshot_dir = create_snapshot(proposal_id)
    copy_shadow_to_active(proposal_id)
    log_change(proposal_id, "promoted", f"snapshot: {snapshot_dir}")
    print(f"\n{proposal_id} promoted to active harness.")


if __name__ == "__main__":
    main()
