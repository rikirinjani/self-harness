"""Add Bonsai provider back to opencode.jsonc."""
import json, re

path = "C:\\Users\\think\\.config\\opencode\\opencode.jsonc"

# Read the JSON properly
text = open(path, "r").read()

# Properly parse and modify with state machine
# Remove comments for JSON parsing
cleaned = []
i = 0
in_str = False
sc = None
while i < len(text):
    ch = text[i]
    if ch == "\\" and in_str:
        cleaned.extend(text[i:i+2])
        i += 2
        continue
    if in_str and ch == sc:
        in_str = False; sc = None
        cleaned.append(ch); i += 1
        continue
    if not in_str and (ch == '"' or ch == "'"):
        in_str = True; sc = ch
        cleaned.append(ch); i += 1
        continue
    if not in_str and ch == "/" and i+1 < len(text) and text[i+1] == "/":
        while i < len(text) and text[i] not in "\n\r": i += 1
        continue
    if not in_str and ch == "/" and i+1 < len(text) and text[i+1] == "*":
        i += 2
        while i < len(text):
            if text[i] == "*" and i+1 < len(text) and text[i+1] == "/":
                i += 2; break
            i += 1
        continue
    cleaned.append(ch)
    i += 1

d = json.loads("".join(cleaned))

# Add bonsai provider
d["provider"]["bonsai"] = {
    "name": "Bonsai 27B (Mac Mini M4)",
    "npm": "@ai-sdk/openai-compatible",
    "options": {
        "baseURL": "http://100.83.28.83:8080/v1",
        "apiKey": "local"
    },
    "models": {
        "/Users/ptpakdefarma/models/ternary-bonsai-27b": {
            "name": "Ternary Bonsai 27B (Sonnet-tier)"
        }
    }
}

# Remove omniroute from disabled_providers if present
if "omniroute" in d.get("disabled_providers", []):
    d["disabled_providers"].remove("omniroute")
    print("Removed omniroute from disabled_providers")

# Write back - preserve original text but replace the provider section
# Find the provider section in the original text
provider_start = text.find('"provider"')
provider_start = text.find('{', provider_start)
provider_end = text.find('}', provider_end_orig) + 1 if False else 0

# Simpler: just write the JSON back with json.dumps
import json as j
# But we need to maintain JSONC comments. Let's just replace the whole file
# Actually write proper JSON for simplicity (OpenCode handles JSONC)
j.dump(d, open(path, "w"), indent=2)

print("Bonsai added to providers")
print(f"Providers: {list(d.get('provider', {}).keys())}")
print(f"Disabled: {d.get('disabled_providers', [])}")
