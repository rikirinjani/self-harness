"""pm1-workspace CLI — scaffold and run ICM-style workspaces."""

import argparse
import os
import shutil
import sys
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "workspace"
WORKSPACES_DIR = Path.cwd() / "workspaces"

AVAILABLE_TEMPLATES = [
    "feature-dev",
]


def cmd_list(args):
    print("Available templates:")
    for t in AVAILABLE_TEMPLATES:
        template_path = TEMPLATES_DIR / t
        desc = ""
        if (template_path / "CONTEXT.md").exists():
            with open(template_path / "CONTEXT.md") as f:
                for line in f:
                    if line.startswith("# "):
                        desc = line.strip("# \n")
                        break
        print(f"  {t:20s} {desc}")

    existing = sorted(WORKSPACES_DIR.glob("*/CONTEXT.md"))
    if existing:
        print("\nExisting workspaces:")
        for p in existing:
            print(f"  {p.parent.name}")


def cmd_scaffold(args):
    template = args.template or "feature-dev"
    template_path = TEMPLATES_DIR / template
    if not template_path.exists():
        print(f"Template not found: {template}. Use --list to see available templates.")
        sys.exit(1)

    target = WORKSPACES_DIR / (args.name or template)
    if target.exists():
        print(f"Workspace already exists: {target}")
        sys.exit(1)

    shutil.copytree(template_path, target)
    print(f"Scaffolded: {target}")
    print(f"  cd workspaces/{target.name}")
    print(f"  pm1-workspace run {target.name} --stage 01")


def cmd_run(args):
    name = args.workspace
    ws_path = WORKSPACES_DIR / name
    if not ws_path.exists():
        print(f"Workspace not found: {name}")
        print(f"  Available: {', '.join(sorted(p.name for p in WORKSPACES_DIR.glob('*/CONTEXT.md')))}")
        sys.exit(1)

    if args.all:
        stages = sorted(
            p.name for p in ws_path.glob("stages/*/CONTEXT.md")
        )
    else:
        stage_str = args.stage.zfill(2)
        stages = [
            f"stages/{stage_str}-{p.name.split('-', 1)[1]}" if "-" in p.name else p.name
            for p in ws_path.glob(f"stages/{stage_str}*/CONTEXT.md")
        ]
        if not stages:
            print(f"Stage not found: {args.stage}. Available stages:")
            existing = sorted(p.parent.name for p in ws_path.glob("stages/*/CONTEXT.md"))
            for s in existing:
                print(f"  {s}")
            sys.exit(1)

    for stage_path in stages:
        stage_dir = ws_path / stage_path
        stage_name = stage_dir.name
        print(f"\n{'='*50}")
        print(f"  Stage: {stage_name}")
        print(f"{'='*50}")

        context_path = stage_dir / "CONTEXT.md"
        output_dir = stage_dir / "output"
        output_dir.mkdir(exist_ok=True)

        if context_path.exists():
            preview = "\n".join(open(context_path).read().splitlines()[:20])
            print(f"\n  Contract preview:\n{preview}\n")

        print(f"\n  To execute: opencode run --context {context_path}")
        print(f"  Output: {output_dir}")

        if args.all:
            input("  Press Enter to continue to next stage...")

    print(f"\n  Pipeline complete for {name}")


def main():
    parser = argparse.ArgumentParser(description="ICM workspace manager")
    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("list", aliases=["ls"], help="List templates and workspaces")

    sp = sub.add_parser("scaffold", help="Create a new workspace")
    sp.add_argument("--template", "-t", choices=AVAILABLE_TEMPLATES, default="feature-dev")
    sp.add_argument("--name", "-n", default="", help="Output name (default: template name)")

    sp = sub.add_parser("run", help="Run one or all stages")
    sp.add_argument("workspace")
    sp.add_argument("--stage", "-s", default="01", help="Stage number (01-99)")
    sp.add_argument("--all", "-a", action="store_true", help="Run all stages sequentially")

    args = parser.parse_args()
    if args.command in ("list", "ls"):
        cmd_list(args)
    elif args.command == "scaffold":
        cmd_scaffold(args)
    elif args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
