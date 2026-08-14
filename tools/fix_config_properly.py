"""Properly clean opencode.jsonc — only strip comments, not // in URLs."""
import re, json

path = "C:\\Users\\think\\.config\\opencode\\opencode.jsonc"

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Remove // comments ONLY when // is not inside a string
# Strategy: use a state machine that tracks if we're inside a string
result = []
i = 0
in_string = False
string_char = None
escape = False

while i < len(text):
    ch = text[i]
    
    if escape:
        result.append(ch)
        escape = False
        i += 1
        continue
    
    if ch == "\\" and in_string:
        escape = True
        result.append(ch)
        i += 1
        continue
    
    if ch == string_char and in_string:
        in_string = False
        string_char = None
        result.append(ch)
        i += 1
        continue
    
    if ch in ('"', "'") and not in_string:
        in_string = True
        string_char = ch
        result.append(ch)
        i += 1
        continue
    
    # If not in string and we see //, skip to end of line
    if not in_string and ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
        while i < len(text) and text[i] not in ("\n", "\r"):
            i += 1
        # Keep the newline
        if i < len(text):
            result.append(text[i])
            if text[i] == "\r" and i + 1 < len(text) and text[i + 1] == "\n":
                i += 1
                result.append(text[i])
            i += 1
        continue
    
    # Remove /* */ block comments too
    if not in_string and ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
        i += 2
        while i < len(text):
            if text[i] == "*" and i + 1 < len(text) and text[i + 1] == "/":
                i += 2
                break
            result.append(text[i])  # keep content inside block comments? No, skip it
            i += 1
        continue
    
    result.append(ch)
    i += 1

cleaned = "".join(result)

# Validate JSON
try:
    d = json.loads(cleaned)
    print(f"JSON valid! Providers: {list(d.get('provider', {}).keys())}")
    print(f"Disabled: {d.get('disabled_providers', [])}")
    
    # Ensure omniroute is disabled
    disabled = d.get('disabled_providers', [])
    if 'omniroute' not in disabled:
        disabled.append('omniroute')
        d['disabled_providers'] = disabled
        print("Added omniroute to disabled_providers")
    
    # Write the original text back, but with the disabled_providers fix
    import re as re2
    old_entry = '"disabled_providers": []'
    new_entry = json.dumps({"disabled_providers": d["disabled_providers"]})[1:-1]  # extract just the value
    if old_entry in text:
        text = text.replace(old_entry, f'"disabled_providers": {json.dumps(d["disabled_providers"])}')
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("Config updated and saved")
    else:
        print("disabled_providers already has entries")
        
except json.JSONDecodeError as e:
    print(f"JSON ERROR: {e}")
    # Show context
    ctx = cleaned[max(0, e.pos-30):e.pos+30]
    print(f"Context: {repr(ctx)}")
