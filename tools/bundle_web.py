"""Web Bundle Generator — package skills as Gemini/ChatGPT-ready markdown.

Usage:
    python tools/bundle_web.py spec-driven-development
    python tools/bundle_web.py --all                          # bundle all skills
    python tools/bundle_web.py --output ./web-bundles         # output dir
    python tools/bundle_web.py --format gemini                # gemini (default) or chatgpt
"""

import os
import re
import sys
import yaml
from pathlib import Path

SKILLS_DIR = Path.home() / ".config" / "opencode" / "skills"
OUTPUT_DIR = Path.cwd() / "web-bundles"


def load_skill(slug: str) -> dict | None:
    path = SKILLS_DIR / slug / "SKILL.md"
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8", errors="replace")

    fm = {}
    body = content.strip()
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                pass
            body = parts[2].strip()

    return {
        "slug": slug,
        "name": fm.get("name", slug),
        "description": fm.get("description", ""),
        "body": body,
        "frontmatter": fm,
    }


def bundle_gemini(skill: dict) -> str:
    lines = []
    lines.append(f"# {skill['name']}")
    lines.append("")
    if skill["description"]:
        lines.append(skill["description"])
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(skill["body"])
    return "\n".join(lines)


def bundle_chatgpt(skill: dict) -> str:
    lines = []
    lines.append(f"You are a {skill['name']} specialist.")
    lines.append("")
    if skill["description"]:
        lines.append(skill["description"])
        lines.append("")
    lines.append("## Instructions")
    lines.append("")
    lines.append(skill["body"])
    lines.append("")
    lines.append("---")
    lines.append("Respond directly and in character. Follow the workflow above.")
    return "\n".join(lines)


def build_index(skills: list[dict]) -> str:
    lines = ["# Web Bundles Index", "",
             "| Skill | Description | Gemini | ChatGPT |", 
             "|-------|-------------|--------|---------|"]
    for s in skills:
        gemini_link = f"[Gemini](./gemini/{s['slug']}.md)"
        chatgpt_link = f"[ChatGPT](./chatgpt/{s['slug']}.md)"
        desc_short = s["description"][:80] + "..." if len(s["description"]) > 80 else s["description"]
        lines.append(f"| {s['name']} | {desc_short} | {gemini_link} | {chatgpt_link} |")
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Package skills as web bundles")
    parser.add_argument("skills", nargs="*", help="Skills to bundle (default: all)")
    parser.add_argument("--all", action="store_true", help="Bundle all skills")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="Output directory")
    parser.add_argument("--format", default="gemini", choices=["gemini", "chatgpt", "both"],
                        help="Output format")
    args = parser.parse_args()

    slugs = args.skills
    if args.all or not slugs:
        slugs = sorted(d.name for d in SKILLS_DIR.iterdir() if d.is_dir())

    skills = []
    for slug in slugs:
        s = load_skill(slug)
        if s:
            skills.append(s)
        else:
            print(f"  [WARN] Skill not found: {slug}")

    out = Path(args.output)
    gemini_dir = out / "gemini"
    chatgpt_dir = out / "chatgpt"
    gemini_dir.mkdir(parents=True, exist_ok=True)
    chatgpt_dir.mkdir(parents=True, exist_ok=True)

    for s in skills:
        if args.format in ("gemini", "both"):
            content = bundle_gemini(s)
            path = gemini_dir / f"{s['slug']}.md"
            path.write_text(content, encoding="utf-8")
            print(f"  [Gemini] {path}")

        if args.format in ("chatgpt", "both"):
            content = bundle_chatgpt(s)
            path = chatgpt_dir / f"{s['slug']}.md"
            path.write_text(content, encoding="utf-8")
            print(f"  [ChatGPT] {path}")

    index = build_index(skills)
    (out / "INDEX.md").write_text(index, encoding="utf-8")
    print(f"\n  Index: {out / 'INDEX.md'}")
    print(f"  {len(skills)} skills bundled")


if __name__ == "__main__":
    main()
