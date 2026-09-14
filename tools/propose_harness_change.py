#!/usr/bin/env python3
"""Automated Harness Change Proposal Generator — Phase 4

Reads the latest JSON weakness miner report and generates a formal harness
improvement proposal from the top-ranked candidate.

Usage:
    python tools/propose_harness_change.py
    python tools/propose_harness_change.py --rank 2
    python tools/propose_harness_change.py --report proposals/weakness-miner-report-YYYY-MM-DD.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
PROPOSALS_DIR = ROOT / "proposals"
TEMPLATE_FILE = PROPOSALS_DIR / "TEMPLATE-harness-improvement.md"


def find_latest_report():
    """Find the most recent weakness miner JSON report."""
    reports = sorted(PROPOSALS_DIR.glob("weakness-miner-report-*.json"), reverse=True)
    if not reports:
        print("No weakness miner JSON reports found in proposals/")
        print("Run: python tools/weakness_miner.py --json --output proposals/weakness-miner-report-YYYY-MM-DD.json")
        sys.exit(1)
    return reports[0]


def next_proposal_id():
    """Find the next P-NNN proposal number."""
    existing = PROPOSALS_DIR.glob("P-*.md")
    nums = []
    for f in existing:
        m = re.match(r"P-(\d+)", f.stem)
        if m:
            nums.append(int(m.group(1)))
    return max(nums, default=0) + 1


def map_theme_to_change(theme):
    """Suggest a harness change based on the weakness theme."""
    text = theme.get("theme", "").lower()
    if "coding" in text or "fixer" in text:
        return (
            "Extend `rules/fixer-workflow.md` with additional self-check steps for coding tasks. "
            "Require the fixer to produce a minimal regression test before marking a bug fix complete.",
            "rules/fixer-workflow.md",
            "BENCH-C-01, BENCH-C-02, BENCH-C-04",
        )
    if "validator" in text or "prompt" in text or "output" in text:
        return (
            "Update `validator/generate_prompts.py` to always embed or reference the actual benchmark output file "
            "and to regenerate prompts automatically after benchmark re-runs.",
            "validator/generate_prompts.py",
            "BENCH-R-01, BENCH-O-04",
        )
    if "failure" in text or "process" in text:
        return (
            "Add a pre-flight process checklist to the orchestrator workflow that verifies trace and failure "
            "recording before any task is marked complete.",
            "rules/orchestrator-workflow.md",
            "BENCH-O-04, BENCH-O-05",
        )
    if "trace" in text:
        return (
            "Migrate legacy `.pm1` trace files to structured `.json` to improve weakness mining accuracy. "
            "Add a trace schema linter to CI.",
            "tools/trace_migrate.py",
            "all benchmarks",
        )
    return (
        "Investigate the ranked weakness theme and implement the smallest harness change that produces "
        "a measurable improvement in the affected benchmarks.",
        "TBD",
        ", ".join(theme.get("benchmarks", [])[:3]) or "TBD",
    )


def generate_proposal(report_path, rank=1):
    """Generate a proposal from the top-ranked candidate in the report."""
    data = json.loads(report_path.read_text(encoding="utf-8"))
    candidates = data.get("ranked_candidates", [])
    if not candidates:
        print("No ranked candidates in report.")
        sys.exit(1)
    if rank > len(candidates):
        print(f"Rank {rank} requested but only {len(candidates)} candidates exist.")
        sys.exit(1)

    theme = candidates[rank - 1]
    pid = f"P-{next_proposal_id():03d}"
    change, target, benchmarks = map_theme_to_change(theme)

    summary = data.get("summary", {})
    evidence_benchmarks = ", ".join(theme.get("benchmarks", [])[:5]) or "N/A"
    evidence_failures = "failures/*.json" if theme.get("source") == "failure" else "N/A"
    evidence_traces = "traces/*.pm1" if theme.get("source") == "trace" else "N/A"

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    proposal = template.replace("{PROPOSAL_ID}", pid)
    proposal = proposal.replace("{W-XXX or benchmark refs}", f"WM-{data['generated'][:10]}-{rank}")
    proposal = proposal.replace("{orchestrator / fixer / designer / explorer / etc.}", "orchestrator / fixer")
    proposal = proposal.replace("{agent or human}", "orchestrator (auto-generated)")
    proposal = proposal.replace("{YYYY-MM-DD}", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    proposal = proposal.replace("{BENCH-X-NN}", benchmarks)
    proposal = proposal.replace("{X.XX}", f"{summary.get('avg_diff', 0):.2f}")
    proposal = proposal.replace("{X.XX}", f"{summary.get('avg_diff', 0):.2f}", 1)
    proposal = proposal.replace("{correctness, completeness, ...}", ", ".join(theme.get("affected_axes", ["faithfulness"])))
    proposal = proposal.replace("failures/{timestamp}-{category}-{slug}.json", evidence_failures)
    proposal = proposal.replace("traces/{slug}.pm1", evidence_traces)
    proposal = proposal.replace("traces/{slug}.pm1 or traces/{slug}.json", evidence_traces)

    # Fill section 2
    section2 = f"""{change}

Target files:
- `{target}`
- `tools/revalidate_benchmarks.py` (for verification)

Expected behavior change: the ranked weakness theme is addressed and the affected benchmark(s) show reduced executor/validator diff on re-validation.
"""
    proposal = re.sub(r"## 2\. Proposed Change\n\n.*?(?=\n\n---\n\n## 3\. Verification Plan)",
                      f"## 2. Proposed Change\n\n{section2}",
                      proposal, flags=re.DOTALL)

    # Fill section 3
    section3 = f"""Primary: {benchmarks}

Expected outcome after change:
- Executor/validator diff for the primary benchmark(s) drops by at least 0.5.
- `tools/revalidate_benchmarks.py` exits 0 for the affected set.
- No regressions in `python benchmarks/run.py --summary`.
"""
    proposal = re.sub(r"## 3\. Verification Plan\n\n.*?(?=\n\n---\n\n## 4\. Risk and Rollback Plan)",
                      f"## 3. Verification Plan\n\n{section3}",
                      proposal, flags=re.DOTALL)

    output_path = PROPOSALS_DIR / f"{pid}-auto-{sanitize(theme['theme'][:40])}.md"
    output_path.write_text(proposal, encoding="utf-8")
    print(f"Generated {output_path}")
    return output_path, theme


def sanitize(text):
    """Make a filename-safe slug from a theme."""
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", text).strip("-").lower()


def main():
    parser = argparse.ArgumentParser(description="Auto-generate harness improvement proposal")
    parser.add_argument("--report", help="Path to weakness miner JSON report")
    parser.add_argument("--rank", type=int, default=1, help="Rank of candidate to turn into proposal")
    args = parser.parse_args()

    report_path = Path(args.report) if args.report else find_latest_report()
    if not report_path.exists():
        print(f"Report not found: {report_path}")
        sys.exit(1)

    output_path, theme = generate_proposal(report_path, args.rank)
    print(f"\nGenerated proposal from candidate #{args.rank}:")
    print(f"  Theme: {theme['theme']}")
    print(f"  Score: {theme['score']}")
    print(f"  Priority: {theme.get('priority', 'low')}")
    print(f"  File: {output_path}")


if __name__ == "__main__":
    main()
