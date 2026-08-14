"""Debug the opencode.jsonc bytes."""
path = "C:\\Users\\think\\.config\\opencode\\opencode.jsonc"

with open(path, "rb") as f:
    raw = f.read()

# Show first 100 bytes as hex
print("First 100 bytes:")
print(raw[:100].hex(" "))

# Show as lines
lines = raw.split(b"\n")
for i, line in enumerate(lines[:5]):
    print(f"\nLine {i+1} ({len(line)} bytes):")
    print(f"  hex: {line[:60].hex(' ')}")
    print(f"  raw: {repr(line[:60])}")
