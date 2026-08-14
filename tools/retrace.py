#!/usr/bin/env python3
"""
retrace.py -- Scan for untraced project work.

Cross-references trace key_files against project files and reports
anything that was never recorded in a trace.

Usage:
    python retrace.py --project-root /path/to/project [--traces-dir /path/to/traces]

If --traces-dir is omitted, defaults to {project-root}/self-harness/traces/.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Defaults — overridden by CLI args
TRACES_DIR   = Path("C:/Users/think/self-harness/traces")
PROJECT_ROOT = Path("C:/Users/think/Project")

SKIP_DIRS = {
    ".git","node_modules","__pycache__",".venv","venv",
    "dist","build",".next","flyer_output","stock_vectors_v1",
    ".github",".githooks","photos","web-bundles","chat-archive",
    "memory","templates",
}
SKIP_EXTS = {
    ".pyc",".pyo",".exe",".dll",".so",".dylib",
    ".png",".jpg",".jpeg",".gif",".webp",".svg",".ico",
    ".mp3",".mp4",".wav",".mov",".avi",
    ".zip",".tar",".gz",".7z",".rar",".bz2",
    ".ttf",".otf",".woff",".woff2",
    ".lock",".map",".idx",".mp4.part",".pk",".pkl",
}
TEXT_EXTS = {
    ".py",".js",".mjs",".ts",".tsx",".jsx",".cjs",
    ".md",".markdown",".rst",".txt",
    ".json",".jsonc",".yaml",".yml",".toml",
    ".html",".css",".scss",".less",
    ".sh",".bash",".ps1",".psm1",
    ".c",".h",".cpp",".hpp",".rs",".go",
    ".java",".kt",".swift",
    ".env",".cfg",".ini",".conf",
    ".csv",".xml",".tex",".bib",
}
NO_EXT = {"Makefile","Dockerfile","LICENSE","CHANGELOG","SKILL.md"}

def is_skip(p: Path) -> bool:
    return bool(SKIP_DIRS & set(p.parts)) or p.suffix.lower() in SKIP_EXTS

def is_text(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXTS or p.name in NO_EXT

def short(p: Path) -> str:
    try: return str(p.relative_to(PROJECT_ROOT)).replace("\\","/")
    except ValueError: return str(p).replace("\\","/")

def norm(path_str: str) -> str:
    """Normalize a key_file string for matching."""
    s = path_str.replace("\\","/").strip("/").lower()
    # Expand ~ to home
    if s.startswith("~/"):
        s = str(Path.home()).replace("\\","/").lower() + "/" + s[2:]
    # Handle C:/Users/think paths
    return s

def is_traced(project_file: Path, traced_paths: set[str], traced_names: set[str]) -> bool:
    """Check if a project file matches any traced key_file."""
    pf_short = short(project_file).lower()
    pf_name  = project_file.name.lower()
    pf_full  = str(project_file).replace("\\","/").lower()

    # Check if the full path or short path is in traced paths
    if pf_full in traced_paths:
        return True
    if pf_short in traced_paths:
        return True

    # Check if the project path contains a traced path as suffix
    for tp in traced_paths:
        if pf_full.endswith("/" + tp) or pf_short.endswith("/" + tp):
            return True

    # Check basename match (for traces that only recorded the filename)
    for tn in traced_names:
        if pf_name.endswith(tn) or tn.endswith(pf_name):
            return True

    return False

# -- Collect traces ---------------------------------------------------

def collect():
    traces = []
    traced_paths = set()
    traced_names = set()

    if not TRACES_DIR.exists():
        return [], set(), set()

    for p in sorted(TRACES_DIR.glob("*")):
        if p.suffix not in (".pm1", ".json"):
            continue
        try:
            with open(p, "r", encoding="utf-8-sig") as f:
                d = json.load(f)
            kf_list = d.get("key_files", [])
            kf_norm = set()
            for kf in kf_list:
                n = norm(str(kf))
                kf_norm.add(n)
                # Extract just the basename
                bn = n.split("/")[-1]
                if bn and len(bn) >= 3:
                    traced_names.add(bn)

            traces.append({
                "action": d.get("action", ""),
                "key_files": kf_norm,
                "agent": d.get("agent",""),
                "outcome": d.get("outcome",""),
            })
            traced_paths.update(kf_norm)
        except Exception:
            pass
    return traces, traced_paths, traced_names

# -- Main ------------------------------------------------------------

def run():
    print("=" * 60)
    print("  retrace -- untraced work scanner")
    print(f"  {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    print()

    traces, traced_paths, traced_names = collect()
    print(f"  Traces loaded:       {len(traces)}")
    print(f"  Unique key_files:    {len(traced_paths)}")
    print(f"  Unique filenames:    {len(traced_names)}")
    print()

    # Scan project
    proj = []
    for p in sorted(PROJECT_ROOT.rglob("*")):
        if p.is_file() and is_text(p) and not is_skip(p):
            proj.append(p)
    print(f"  Project text files:  {len(proj)}")
    print()

    # Cross-reference
    untraced = []
    for pf in proj:
        if not is_traced(pf, traced_paths, traced_names):
            untraced.append(pf)

    if not untraced:
        print("  RESULT: All project files appear in at least one trace.")
        print("          Directory is trace-clean.")
        print()
        return

    print(f"  UNTRACED: {len(untraced)} file(s)")
    print()

    # Group by top-level directory
    groups = {}
    for uf in untraced:
        s = short(uf)
        top = s.split("/")[0] if "/" in s else "(root)"
        groups.setdefault(top, []).append((uf, s))

    for grp in sorted(groups.keys()):
        files = groups[grp]
        print(f"  [{grp}/] ({len(files)} files)")
        for uf, s in files[:15]:
            try:
                mt = datetime.fromtimestamp(uf.stat().st_mtime, tz=timezone.utc)
                ts = mt.strftime("%Y-%m-%d %H:%M")
            except OSError:
                ts = "unknown     "
            print(f"    [{ts}]  {s}")
        if len(files) > 15:
            print(f"    ... and {len(files) - 15} more")
        print()

    print(f"  To retroactively trace:")
    print(f"    pm1-trace trace --agent <role> --outcome pass \\")
    print(f"      --slug retrace-<name> --action \"...\" --key-files <files>")
    print()
    print(f"  Total untraced: {len(untraced)}")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="retrace — find untraced project work by cross-referencing trace key_files",
    )
    parser.add_argument(
        "--project-root", type=Path, default=PROJECT_ROOT,
        help=f"Project directory to scan (default: {PROJECT_ROOT})",
    )
    parser.add_argument(
        "--traces-dir", type=Path, default=None,
        help="Trace directory (default: <project-root>/self-harness/traces/)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show which traces were loaded and their key_files",
    )
    args = parser.parse_args()

    PROJECT_ROOT = args.project_root.resolve()
    if args.traces_dir:
        TRACES_DIR = args.traces_dir.resolve()
    elif not TRACES_DIR.is_dir():
        # Hardcoded default doesn't exist — try project-relative
        candidate = PROJECT_ROOT / "self-harness" / "traces"
        if candidate.is_dir():
            TRACES_DIR = candidate

    if args.verbose:
        print(f"  traces dir:  {TRACES_DIR}")
        print(f"  project dir: {PROJECT_ROOT}")
        print()

    run()
