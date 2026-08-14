"""Verify OMOS model routing matches opencode.jsonc providers."""
import json, re

# Load OMOS config
omo = json.load(open("C:\\Users\\think\\.config\\opencode\\oh-my-opencode-slim.json"))
preset_name = omo.get("preset")
print(f"Active preset: {preset_name}")

preset = omo.get("presets", {}).get(preset_name, {})
print(f"Agents: {len(preset)}")
for agent, cfg in preset.items():
    print(f"  {agent:15s} -> {cfg.get('model', '?')}")

# Parse opencode.jsonc provider list
text = open("C:\\Users\\think\\.config\\opencode\\opencode.jsonc").read()
# Simple state machine to strip comments
cleaned = []
i = 0
in_str = False
sc = None
while i < len(text):
    ch = text[i]
    if ch == "\\" and in_str:
        cleaned.append(ch)
        i += 1
        if i < len(text):
            cleaned.append(text[i])
        i += 1
        continue
    if in_str and ch == sc:
        in_str = False
        sc = None
        cleaned.append(ch)
        i += 1
        continue
    if not in_str and (ch == '"' or ch == "'"):
        in_str = True
        sc = ch
        cleaned.append(ch)
        i += 1
        continue
    if not in_str and ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
        while i < len(text) and text[i] not in "\n\r":
            i += 1
        continue
    if not in_str and ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
        i += 2
        while i < len(text):
            if text[i] == "*" and i + 1 < len(text) and text[i + 1] == "/":
                i += 2
                break
            i += 1
        continue
    cleaned.append(ch)
    i += 1

oc = json.loads("".join(cleaned))

# List provider model IDs
print("\nProvider models available:")
for pname, pcfg in oc.get("provider", {}).items():
    models = list(pcfg.get("models", {}).keys())
    print(f"  {pname:15s} -> {models}")

# Cross-reference: check each OMOS model ref exists
print("\nCross-reference check:")
for agent, cfg in preset.items():
    model_ref = cfg.get("model", "")
    if "/" in model_ref:
        prov, model = model_ref.split("/", 1)
        prov_config = oc.get("provider", {}).get(prov)
        if prov_config:
            if model in prov_config.get("models", {}):
                print(f"  {agent:15s} OK  -> {model_ref}")
            else:
                print(f"  {agent:15s} WARN -> model '{model}' not found in provider '{prov}'")
                print(f"         Available: {list(prov_config.get('models', {}).keys())}")
        else:
            print(f"  {agent:15s} FAIL -> provider '{prov}' not found in opencode.jsonc!")

# Check disabled providers
disabled = oc.get("disabled_providers", [])
print(f"\nDisabled providers: {disabled}")

# Check Gemini API key status
gemini_key = oc.get("provider", {}).get("gemini", {}).get("options", {}).get("apiKey", "")
print(f"\nGemini API key: {'SET' if gemini_key else 'EMPTY - needs key'}")
print(f"OpenRouter key: {'SET' if oc.get('provider',{}).get('openrouter',{}).get('options',{}).get('apiKey','') != 'sk-or-placeholder-replace-with-your-key' else 'PLACEHOLDER - needs real key'}")

print("\n=== VERDICT ===")
all_ok = True
for agent, cfg in preset.items():
    model_ref = cfg.get("model", "")
    if "/" in model_ref:
        prov, model = model_ref.split("/", 1)
        if prov in oc.get("provider", {}) and model in oc.get("provider", {}).get(prov, {}).get("models", {}):
            continue
        all_ok = False
        break

if all_ok:
    print("All agent model references resolve correctly. Routing should work.")
else:
    print("Some model references need fixing.")
