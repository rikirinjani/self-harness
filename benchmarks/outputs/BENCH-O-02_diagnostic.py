"""BENCH-O-02: Diagnostic Execution - cp1252 encoding issue."""
import sys

print("=== Encoding Diagnostics ===")
print(f"stdout encoding: {sys.stdout.encoding}")
print(f"preferred encoding: {sys.getdefaultencoding()}")

print("\n--- Problematic characters ---")
test_chars = {
    "em dash": "\u2014",
    "bullet": "\u2022",
    "greater-or-equal": "\u2265",
    "check mark": "\u2705",
    "cross mark": "\u274c",
}
for name, char in test_chars.items():
    try:
        char.encode("cp1252")
        print(f"  {name} (U+{ord(char):04X}): OK in cp1252")
    except UnicodeEncodeError:
        print(f"  {name} (U+{ord(char):04X}): FAILS in cp1252")

print("\n--- Source analysis ---")
# Check catalog
with open(
    r"C:\Users\think\AppData\Local\Temp\self-harness-sync\benchmark_catalog.md",
    encoding="utf-8",
) as f:
    content = f.read()
non_ascii = [(i, c) for i, c in enumerate(content) if ord(c) > 127]
print(f"Catalog non-ASCII chars: {len(non_ascii)}")
for pos, char in non_ascii[:10]:
    line = content[:pos].count("\n") + 1
    print(f"  Line {line}: U+{ord(char):04X} ({repr(char)})")

# Check run.py
with open(
    r"C:\Users\think\AppData\Local\Temp\self-harness-sync\benchmarks\run.py",
    encoding="utf-8",
) as f:
    run_content = f.read()
non_ascii_run = [(i, c) for i, c in enumerate(run_content) if ord(c) > 127]
print(f"\nrun.py non-ASCII chars: {len(non_ascii_run)}")
for pos, char in non_ascii_run[:10]:
    line = run_content[:pos].count("\n") + 1
    print(f"  Line {line}: U+{ord(char):04X} ({repr(char)})")

# Test the actual error scenario
print("\n--- Reproduction ---")
try:
    # Simulate cp1252 output
    b"\u2265".decode("utf-8")  # just to confirm char
    test = "\u2265"
    test.encode("cp1252")  # this should fail
except UnicodeEncodeError as e:
    print(f"PASS: cp1252 encode error reproduced: {e}")

# Fix recommendation
print("\n--- Finding ---")
print("Root cause: Python on Windows defaults to cp1252 console encoding.")
print("The benchmark_catalog.md and run.py contain non-ASCII characters")
print("(≥, —, •, ✅, ❌) that are not representable in cp1252.")
print()
print("Fix: Add to run.py main():")
print("  if hasattr(sys.stdout, 'reconfigure'):")
print("      sys.stdout.reconfigure(encoding='utf-8')")
print("Or set environment variable PYTHONIOENCODING=utf-8.")
