"""Fix opencode.jsonc: remove control chars, disable omniroute, verify JSON."""
import json, re

path = "C:\\Users\\think\\.config\\opencode\\opencode.jsonc"
text = open(path, "r", encoding="utf-8").read()

# Remove all control characters except newlines, tabs, carriage returns
orig_len = len(text)
text = "".join(ch if ord(ch) >= 32 or ch in "\n\r\t" else "" for ch in text)
removed = orig_len - len(text)
if removed:
    print(f"Removed {removed} control character(s)")

# Add omniroute to disabled_providers
old = '"disabled_providers": []'
new = '"disabled_providers": ["omniroute"]'
if old in text:
    text = text.replace(old, new)
    print("Added omniroute to disabled_providers")
elif '"omniroute"' in text:
    print("omniroute already disabled")

# Remove any remaining 9router references (safety)
if "9router" in text.lower():
    text = re.sub(r'(?i)9router', '', text)
    print("Removed 9router references")

# Verify JSON parses (strip comments first for validation)
import re as re2
stripped = re2.sub(r'//.*', '', text)
stripped = re2.sub(r'/\*.*?\*/', '', stripped, flags=re2.DOTALL)
try:
    d = json.loads(stripped)
    print(f"JSON valid. Providers: {list(d.get('provider', {}).keys())}")
    print(f"Disabled: {d.get('disabled_providers', [])}")
except json.JSONDecodeError as e:
    print(f"JSON ERROR: {e}")
    lines = text[:e.pos].split("\n")
    print(f"Near line {len(lines)}")

# Write back
open(path, "w", encoding="utf-8").write(text)
print("Config updated")
