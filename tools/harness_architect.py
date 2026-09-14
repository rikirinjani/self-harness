#!/usr/bin/env python3
"""Harness Architect — Phase 5

Reads an approved proposal JSON file and generates a concrete harness diff
inside the shadow/ directory.

Usage:
    python tools/harness_architect.py proposals/json/P-004.json
    python tools/harness_architect.py --proposal P-004 --shadow-dir shadow
"""

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SHADOW_DIR = ROOT / "shadow"
SHADOW_RULES = SHADOW_DIR / "rules"


def load_proposal(path):
    if not path.exists():
        print(f"Proposal not found: {path}")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def generate_diff(proposal, shadow_dir):
    """Generate harness diffs in shadow/ based on proposal type."""
    target_files = proposal.get("change", {}).get("target_files", [])
    generated = []

    for target in target_files:
        if target.startswith("rules/"):
            rule_name = Path(target).name
            shadow_path = shadow_dir / "rules" / rule_name
            if not shadow_path.exists():
                shadow_path.write_text(generate_rule_file(proposal), encoding="utf-8")
                generated.append(str(shadow_path))
            else:
                patch_rule_file(shadow_path, proposal)
                generated.append(str(shadow_path))
        elif target.startswith("tools/"):
            tool_name = Path(target).name
            shadow_tool = shadow_dir / "tools" / tool_name
            shadow_tool.parent.mkdir(parents=True, exist_ok=True)
            shadow_tool.write_text(generate_tool_stub(proposal), encoding="utf-8")
            generated.append(str(shadow_tool))
        elif target.startswith("validator/"):
            # Prompt-level changes are applied via validator/generate_prompts.py; no direct file.
            pass

    return generated


def generate_rule_file(proposal):
    """Create a new shadow rule file from a proposal."""
    title = proposal.get("proposal_id", "P-???")
    desc = proposal.get("change", {}).get("description", "No description")
    agent = proposal.get("affected_agent", "orchestrator")
    return f"""# {agent.title()} Workflow Rule — {title}

**Version:** 1.0
**Status:** Shadow
**Applies to:** All {agent} tasks
**Owner:** self-harness program

---

## Purpose

{desc}

---

## Generated Requirements

This rule is auto-generated from {title}. Before deployment, a human must review
and approve the shadow-mode benchmark results.

---

## Rollback

Revert the shadow rule file and remove it from the active rules directory.
"""


def patch_rule_file(path, proposal):
    """Patch an existing shadow rule file with new requirements."""
    text = path.read_text(encoding="utf-8")
    title = proposal.get("proposal_id", "P-???")
    desc = proposal.get("change", {}).get("description", "No description")
    addition = f"\n\n### {title} (shadow addition)\n\n{desc}\n"
    if addition not in text:
        text += addition
    path.write_text(text, encoding="utf-8")


def generate_tool_stub(proposal):
    """Generate a stub shadow tool from a proposal."""
    tool_name = Path(proposal.get("change", {}).get("target_files", [""])[0]).stem
    return f"""#!/usr/bin/env python3
\"\"\"{tool_name} — shadow implementation from {proposal.get('proposal_id', 'P-???')}

{proposal.get('change', {{}}).get('description', 'No description')}
\"\"\"

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# TODO: implement the helper logic here.

if __name__ == "__main__":
    print("{tool_name} shadow stub")
"""


def main():
    parser = argparse.ArgumentParser(description="Generate shadow harness diffs from a proposal")
    parser.add_argument("proposal", help="Path to proposal JSON file or P-NNN id")
    parser.add_argument("--shadow-dir", default=str(SHADOW_DIR), help="Shadow harness directory")
    args = parser.parse_args()

    if not args.proposal.endswith(".json"):
        proposal_path = ROOT / "proposals" / "json" / f"{args.proposal}.json"
    else:
        proposal_path = Path(args.proposal)

    proposal = load_proposal(proposal_path)
    shadow_dir = Path(args.shadow_dir)
    shadow_dir.mkdir(parents=True, exist_ok=True)

    generated = generate_diff(proposal, shadow_dir)
    print(f"Generated {len(generated)} shadow diff(s) for {proposal['proposal_id']}:")
    for g in generated:
        print(f"  - {g}")


if __name__ == "__main__":
    main()
