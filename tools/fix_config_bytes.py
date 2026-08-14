"""Debug control characters in opencode.jsonc."""
import json, re

path = "C:\\Users\\think\\.config\\opencode\\opencode.jsonc"

# Read as binary to find control chars
with open(path, "rb") as f:
    raw = f.read()

# Show line 2
lines = raw.split(b"\n")
print(f"Total lines: {len(lines)}")
print(f"Line 2 raw: {repr(lines[1][:80])}")
print(f"Line 2 hex: {lines[1][:40].hex(' ')}")

# Find all control characters
for i, byte in enumerate(raw):
    if byte < 32 and byte not in (10, 13, 9):  # not \n \r \t
        ctx_start = max(0, i - 10)
        ctx_end = min(len(raw), i + 20)
        print(f"\nControl byte 0x{byte:02x} at position {i}")
        print(f"  Context: {repr(raw[ctx_start:ctx_end])}")
        print(f"  Hex: {raw[ctx_start:ctx_end].hex(' ')}")

# Read as text and clean
text = raw.decode("utf-8", errors="replace")
cleaned = "".join(ch if ord(ch) >= 32 or ch in "\n\r\t" else "" for ch in text)

# Strip comments for JSON validation
stripped = re.sub(r"//.*", "", cleaned)
stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)

try:
    d = json.loads(stripped)
    print(f"\nJSON valid! Providers: {list(d.get('provider', {}).keys())}")
    print(f"Disabled: {d.get('disabled_providers', [])}")
except json.JSONDecodeError as e:
    print(f"\nJSON ERROR after cleaning: {e}")
    after_clean = cleaned[:e.pos]
    lines_after = after_clean.split("\n")
    print(f"Near line {len(lines_after)}")
    print(f"Context: {repr(cleaned[max(0,e.pos-20):e.pos+20])}")

# Write cleaned version back
with open(path, "w", encoding="utf-8") as f:
    f.write(cleaned)
print(f"\nWrote cleaned config ({len(cleaned)} chars)")
