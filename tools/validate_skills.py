"""Skill Validator — 2-pass validation for OpenCode skills.

Pass 1: Deterministic checks (frontmatter, naming, files exist)
Pass 2: Inference checks (path resolution, variable references, quality)

Usage:
    python tools/validate_skills.py                          # validate all skills
    python tools/validate_skills.py --skill context-engineering  # single skill
    python tools/validate_skills.py --json                    # JSON output
"""

import os
import re
import sys
import json
import yaml
from pathlib import Path

SKILLS_DIR = Path.home() / ".config" / "opencode" / "skills"
MAX_BODY_LINES = 500
MAX_DESC_LENGTH = 1024
MAX_FM_LINES = 60

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
CRITICAL = "CRITICAL"
HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"

findings = []


def find(name: str, severity: str, rule: str, file: str, detail: str, fix: str):
    findings.append({
        "skill": name, "severity": severity, "rule": rule,
        "file": file, "detail": detail, "fix": fix,
    })


def check_skill(skill_dir: Path):
    slug = skill_dir.name
    skill_path = skill_dir / "SKILL.md"
    has_skill_md = skill_path.exists()

    # SKILL-01: SKILL.md must exist
    if not has_skill_md:
        find(slug, CRITICAL, "SKILL-01", f"{slug}/SKILL.md",
             "Skill directory missing SKILL.md",
             f"Create {slug}/SKILL.md as the skill entrypoint")
        return  # can't check further

    if not skill_path.is_file():
        find(slug, CRITICAL, "SKILL-01", f"{slug}/SKILL.md",
             "SKILL.md is not a file", "")
        return

    content = skill_path.read_text(encoding="utf-8", errors="replace")

    # Parse frontmatter
    fm = {}
    body = content.strip()
    has_fm = content.startswith("---")

    if has_fm:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError as e:
                find(slug, CRITICAL, "SKILL-02", f"{slug}/SKILL.md",
                     f"YAML parse error: {e}", "Fix YAML frontmatter syntax")
            body = parts[2].strip()

    # SKILL-07: Body must be non-empty
    if not body:
        find(slug, MEDIUM, "SKILL-07", f"{slug}/SKILL.md",
             "No body content after frontmatter",
             "Add markdown body with skill instructions")

    # SKILL-02: name must exist
    name = fm.get("name", "")
    if not name:
        find(slug, CRITICAL, "SKILL-02", f"{slug}/SKILL.md",
             "Missing 'name' in frontmatter",
             "Add name: <skill-name> to frontmatter")

    # SKILL-03: description must exist
    desc = fm.get("description", "")
    if not desc:
        find(slug, CRITICAL, "SKILL-03", f"{slug}/SKILL.md",
             "Missing 'description' in frontmatter",
             "Add description: '<what it does and when to use it>' to frontmatter")

    # SKILL-04: name format
    if name and not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        find(slug, HIGH, "SKILL-04", f"{slug}/SKILL.md",
             f"name '{name}' not lowercase-with-hyphens",
             "Use only lowercase, numbers, and hyphens")

    # SKILL-05: name matches directory
    if name and name != slug:
        find(slug, HIGH, "SKILL-05", f"{slug}/SKILL.md",
             f"name '{name}' != directory '{slug}'",
             f"Rename name to '{slug}' or rename directory to '{name}'")

    # SKILL-06: description quality
    if desc:
        if len(desc) > MAX_DESC_LENGTH:
            find(slug, MEDIUM, "SKILL-06", f"{slug}/SKILL.md",
                 f"description too long ({len(desc)} > {MAX_DESC_LENGTH})",
                 "Shorten description")
        if not any(p in desc.lower() for p in ["use when", "use for", "use if", "triggers on"]):
            find(slug, MEDIUM, "SKILL-06", f"{slug}/SKILL.md",
                 "description lacks trigger phrase ('Use when', 'Use for')",
                 "Add 'Use when...' clause to description")

    # SKILL-07: frontmatter lines
    if has_fm and len(parts[1].splitlines()) > MAX_FM_LINES:
        find(slug, LOW, "SKILL-07", f"{slug}/SKILL.md",
             f"frontmatter too long ({len(parts[1].splitlines())} > {MAX_FM_LINES})",
             "Move detailed config to separate files")

    # Body length
    body_lines = body.splitlines()
    if len(body_lines) > MAX_BODY_LINES:
        find(slug, LOW, "SKILL-07", f"{slug}/SKILL.md",
             f"body too long ({len(body_lines)} > {MAX_BODY_LINES} lines)",
             "Consider splitting into reference files")

    # Check for internal file references
    refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', body)
    for text, path in refs:
        if path.startswith("http"):
            continue
        if path.startswith("#"):
            continue
        if path.startswith("{"):
            continue
        resolved = (skill_dir / path).resolve()
        if not resolved.exists():
            find(slug, HIGH, "REF-02", f"{slug}/SKILL.md",
                 f"broken link: [{text}]({path}) -> {resolved}",
                 f"Fix path to '{path}' or create missing file at {resolved}")

    # Check for absolute paths
    abs_refs = re.findall(r'\]\((/[^)]+)\)', body)
    for path in abs_refs:
        find(slug, HIGH, "PATH-01", f"{slug}/SKILL.md",
             f"absolute path reference: {path}",
             "Use relative paths (./ or ../) instead of absolute")

    # Check for banned skip patterns
    skip_patterns = [r'\bskip\s+to\s+step',
                     r'\bskip\s+ahead\b',
                     r'\boptimize\s+the\s+order\b',
                     r'\byou\s+may\s+skip\b']
    for pat in skip_patterns:
        for m in re.finditer(pat, body, re.IGNORECASE):
            if "NEVER" in body[max(0, m.start()-50):m.start()]:
                continue
            find(slug, HIGH, "SEQ-01", f"{slug}/SKILL.md",
                 f"skip instruction: '...{m.group()}...'",
                 "Remove skip instructions — sequential execution is mandatory")

    # Check for time estimates
    time_pats = [r'takes?\s+\d+\s*(min|second|hour|sec)',
                 r'~\d+\s*min', r'estimated\s*time', r'ETA']
    for pat in time_pats:
        for m in re.finditer(pat, body, re.IGNORECASE):
            find(slug, LOW, "SEQ-02", f"{slug}/SKILL.md",
                 f"time estimate: '{m.group()}'",
                 "Remove time estimates — AI execution speed varies")

    # Check for installed_path anti-pattern
    if "{installed_path}" in content:
        find(slug, HIGH, "PATH-02", f"{slug}/SKILL.md",
             "Uses {installed_path} — anti-pattern",
             "Replace {installed_path}/path with ./path (relative)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate OpenCode skills")
    parser.add_argument("--skill", default="", help="Single skill to validate")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.skill:
        dirs = [SKILLS_DIR / args.skill]
    else:
        dirs = sorted(SKILLS_DIR.iterdir())

    for d in dirs:
        if d.is_dir():
            check_skill(d)

    # Summary
    by_severity = {}
    for f in findings:
        by_severity.setdefault(f["severity"], 0)
        by_severity[f["severity"]] += 1

    if args.json:
        print(json.dumps({
            "total_skills": len(dirs),
            "total_findings": len(findings),
            "by_severity": by_severity,
            "findings": findings,
        }, indent=2))
        return

    print(f"\n  Validated {len(dirs)} skills, {len(findings)} findings\n")
    for sev in [CRITICAL, HIGH, MEDIUM, LOW]:
        count = by_severity.get(sev, 0)
        print(f"  {sev}: {count}")
    print()

    for f in findings:
        print(f"  [{f['severity']}] {f['skill']}: {f['rule']} — {f['detail']}")
        print(f"         Fix: {f['fix']}")
        print()

    if len(findings) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
