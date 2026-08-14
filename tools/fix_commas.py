"""Fix missing commas in opencode.jsonc after provider purge."""
import json, re

path = "C:\\Users\\think\\.config\\opencode\\opencode.jsonc"
text = open(path, "r").read()

# Find places where a provider's closing } is followed by "providername" without a comma
# The pattern is: \n    }\n"providername": {
# It should be: \n    },\n"providername": {

text = re.sub(r'\}\s*\n\s*"deepseek"', r'},\n    "deepseek"', text)

open(path, "w").write(text)
print("Fixed")

# Validate
stripped = re.sub(r"//.*", "", text)
stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
try:
    d = json.loads(stripped)
    print(f"Valid! Providers: {list(d.get('provider', {}).keys())}")
    print(f"Disabled: {d.get('disabled_providers', [])}")
except json.JSONDecodeError as e:
    print(f"Still broken at char {e.pos}: {e}")
    ctx = text[max(0,e.pos-30):e.pos+30]
    print(f"Context: {repr(ctx)}")
