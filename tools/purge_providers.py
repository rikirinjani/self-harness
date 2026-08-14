"""Purge all providers except deepseek and opencode-go from opencode.jsonc.
Revert OMOS vision preset to deepseek."""
import json, re

# === 1. OMOS config: set preset to deepseek ===
omos_path = "C:\\Users\\think\\.config\\opencode\\oh-my-opencode-slim.json"
omos = json.load(open(omos_path))
omos["preset"] = "deepseek"
json.dump(omos, open(omos_path, "w"), indent=2)
print("OMOS: preset set to 'deepseek'")

# === 2. opencode.jsonc: remove all providers except deepseek and opencode-go ===
oc_path = "C:\\Users\\think\\.config\\opencode\\opencode.jsonc"
text = open(oc_path, "r", encoding="utf-8").read()

# State machine to find and remove provider blocks
providers_to_remove = ["gemini", "groq", "nvidia", "agnes", "openrouter", "omniroute", "bonsai"]

for prov in providers_to_remove:
    # Match from the provider key through its closing }
    # Pattern: `<whitespace>"prov-name": { ... }`
    pattern = re.compile(
        r'\n\s*"' + re.escape(prov) + r'":\s*\{[^}]*?\}',
        re.DOTALL
    )
    count = 0
    # Need to handle nested braces properly - use a simple approach
    # Find the key start and match balanced braces
    start = text.find(f'"{prov}"')
    if start == -1:
        print(f"  {prov}: not found")
        continue
    
    # Find the colon after the key
    colon = text.find(":", start)
    if colon == -1:
        continue
    
    # Find the opening brace of the value
    brace_start = text.find("{", colon)
    if brace_start == -1:
        continue
    
    # Count braces to find matching close
    depth = 0
    end = brace_start
    for i in range(brace_start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    # Find the line start (go back to previous newline)
    line_start = text.rfind("\n", 0, start)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1  # keep the newline
    
    # Find the comma or newline after the closing brace
    after_end = end
    while after_end < len(text) and text[after_end] in " \t\n\r,":
        after_end += 1
    
    # Remove from line_start to after_end (including trailing comma)
    block = text[line_start:after_end]
    text = text[:line_start] + text[after_end:]
    
    # Clean up double commas or empty lines
    text = text.replace(",\n\n", "\n").replace(",,\n", ",\n")
    
    print(f"  {prov}: purged ({len(block)} bytes)")

# Clean up any double commas or trailing commas before closing braces
text = re.sub(r",\s*}", "}", text)
text = re.sub(r",\s*\]", "]", text)

open(oc_path, "w", encoding="utf-8").write(text)
print(f"\nopencode.jsonc updated ({len(text)} chars)")

# === 3. Save purged provider data to memory ===
# (already in knowledge graph from earlier session)
print("\nProvider data preserved in knowledge graph for future re-enable.")
print("\nDone. Restart OpenCode for changes to take effect.")
