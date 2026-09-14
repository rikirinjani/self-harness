#!/usr/bin/env python3
"""Rollback Harness Change — Phase 6

Restores active harness rules from a snapshot created during promotion.

Usage:
    python tools/rollback_harness_change.py P-004
    python tools/rollback_harness_change.py shadow/snapshots/P-004-YYYYMMDD-HHMMSS
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SHADOW_DIR = ROOT / "shadow"
SHADOW_SNAPSHOTS = SHADOW_DIR / "snapshots"
ACTIVE_RULES = ROOT / "rules"
CHANGELOG = SHADOW_DIR / "CHANGELOG.md"


def find_snapshot(identifier):
    """Resolve P-NNN id or snapshot path."""
    if Path(identifier).exists():
        return Path(identifier)
    candidates = sorted(SHADOW_SNAPSHOTS.glob(f"{identifier}-*"), reverse=True)
    if not candidates:
        print(f"No snapshot found for {identifier}")
        sys.exit(1)
    return candidates[0]


def restore_snapshot(snapshot_dir):
    """Copy snapshot rules back to active rules."""
    snapshot_rules = snapshot_dir / "rules"
    if not snapshot_rules.exists():
        print(f"Snapshot has no rules directory: {snapshot_dir}")
        sys.exit(1)
    if ACTIVE_RULES.exists():
        shutil.rmtree(ACTIVE_RULES)
    shutil.copytree(snapshot_rules, ACTIVE_RULES)
    print(f"Restored active rules from {snapshot_dir}")


def verify_active():
    """Run a lightweight check that active harness is functional."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "benchmarks" / "run.py"), "--summary"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        print(f"Verification failed:\n{result.stderr}")
        return False
    print("Active harness verification passed.")
    return True


def log_change(proposal_id, action, details=""):
    """Append to shadow changelog."""
    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {datetime.now(timezone.utc).isoformat()}Z | {action} | {proposal_id} | {details}\n"
    if CHANGELOG.exists():
        CHANGELOG.write_text(CHANGELOG.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        CHANGELOG.write_text(f"# Shadow Harness Changelog\n\n{line}", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Roll back a harness change")
    parser.add_argument("identifier", help="Proposal id (P-NNN) or snapshot path")
    args = parser.parse_args()

    snapshot_dir = find_snapshot(args.identifier)
    proposal_id = snapshot_dir.name.split("-")[0]
    restore_snapshot(snapshot_dir)
    ok = verify_active()
    log_change(proposal_id, "rolled_back", f"snapshot: {snapshot_dir}, verified: {ok}")
    if not ok:
        print("Rollback restored files but active harness verification failed. Manual inspection required.")
        sys.exit(1)
    print(f"\n{proposal_id} rolled back successfully.")


if __name__ == "__main__":
    main()
