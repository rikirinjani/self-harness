import json
from pathlib import Path

fail_dir = Path("C:/Users/think/self-harness/failures")
files = sorted(fail_dir.glob("*.json"))
categories = {}

for f in files:
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        cat = data.get("category", data.get("trigger", "unknown"))
        agent = data.get("agent", "unknown")
        rc = data.get("root_cause", data.get("description", ""))
        categories.setdefault(cat, []).append({"file": f.name, "agent": agent, "cause_preview": str(rc)[:80]})
    except Exception as e:
        categories.setdefault("parse_error", []).append({"file": f.name, "error": str(e)})

for cat, items in sorted(categories.items()):
    print(f"\n# {cat.upper()} ({len(items)} failures)")
    for item in items[:5]:
        print(f"  {item['file']}")
        if "cause_preview" in item:
            print(f"    agent={item['agent']}  cause={item['cause_preview']}")
        if "error" in item:
            print(f"    ERROR: {item['error']}")
    if len(items) > 5:
        print(f"  ... +{len(items)-5} more")

print(f"\n\nTotal: {len(files)} failures, {len(categories)} categories")
