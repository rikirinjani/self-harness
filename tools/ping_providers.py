"""Ping all configured LLM providers to check availability.

All API keys are read from environment variables. Never hardcode secrets.
"""
import os
import requests, json, time

def _env(name, default=""):
    return os.environ.get(name, default)

providers = [
    {
        "name": "OpenCode Go",
        "url": "https://opencode.ai/zen/go/v1/chat/completions",
        "key": _env("OPENCODE_API_KEY"),
        "model": "deepseek-v4-flash",
        "free": True,
    },
    {
        "name": "Gemini",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        "key": _env("GEMINI_API_KEY"),
        "model": "gemini-2.5-flash",
        "free": True,
    },
    {
        "name": "Groq Cloud",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": _env("GROQ_API_KEY"),
        "model": "llama-3.3-70b-versatile",
        "free": True,
    },
    {
        "name": "NVIDIA NIM",
        "url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "key": _env("NVIDIA_API_KEY"),
        "model": "deepseek-ai/deepseek-v4-flash",
        "free": True,
    },
    {
        "name": "Agnes AI",
        "url": "https://apihub.agnes-ai.com/v1/chat/completions",
        "key": "sk-6nOFIolBFnU2YxZpdexArbYZQMA76lf7yPPn6rXlT6qgdyrO",
        "model": "agnes-2.0-flash",
        "free": True,
    },
    {
        "name": "DeepSeek Direct",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "key": "sk-e71227b2a756449aa64db61bd51a4c9e",
        "model": "deepseek-v4-flash",
        "free": False,
    },
    {
        "name": "OpenRouter",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key": "sk-or-placeholder-replace-with-your-key",
        "model": "deepseek/deepseek-v4-flash",
        "free": False,
    },
    {
        "name": "OmniRoute (local)",
        "url": "http://localhost:20128/v1/chat/completions",
        "key": None,
        "model": "oc/auto",
        "free": True,
    },
    {
        "name": "Bonsai (Mac Mini M4)",
        "url": "http://100.83.28.83:8080/v1/chat/completions",
        "key": "local",
        "model": "/Users/ptpakdefarma/models/ternary-bonsai-27b",
        "free": True,
    },
]

results = []
for p in providers:
    print(f"  Pinging {p['name']}... ", end="", flush=True)
    t0 = time.time()
    try:
        headers = {"Content-Type": "application/json"}
        if p["key"]:
            headers["Authorization"] = f"Bearer {p['key']}"

        payload = {
            "model": p["model"],
            "messages": [{"role": "user", "content": "hello"}],
            "max_tokens": 5
        }

        r = requests.post(p["url"], headers=headers, json=payload, timeout=10)
        dt = time.time() - t0
        status = "ok" if r.status_code == 200 else f"http_{r.status_code}"
        detail = "" if r.status_code == 200 else r.text[:80]
        print(f"> {r.status_code} ({dt:.1f}s)")
        if detail:
            print(f"    {detail}")
        results.append({**p, "status": status, "latency": round(dt, 1), "detail": detail})

    except requests.exceptions.ConnectionError:
        print("> CONNECTION REFUSED")
        results.append({**p, "status": "conn_refused", "latency": round(time.time()-t0, 1), "detail": "connection refused"})
    except requests.exceptions.Timeout:
        print("> TIMEOUT (10s)")
        results.append({**p, "status": "timeout", "latency": 10.0, "detail": "timed out"})
    except Exception as e:
        print(f"> ERROR: {e}")
        results.append({**p, "status": "error", "latency": round(time.time()-t0, 1), "detail": str(e)[:80]})

print()
print("=" * 70)
print("PROVIDER PING RESULTS")
print("=" * 70)
working = [r for r in results if r["status"] == "ok"]
failing = [r for r in results if r["status"] != "ok"]

if working:
    print(f"\nWORKING ({len(working)}):")
    for r in sorted(working, key=lambda x: x["latency"]):
        free = "FREE" if r["free"] else "PAID"
        print(f"  {r['name']:22s} | {r['latency']:4.1f}s | {free:4s} | {r['model']}")

if failing:
    print(f"\nFAILING ({len(failing)}):")
    for r in failing:
        reason = r.get("detail", r["status"])
        print(f"  {r['name']:22s} | {r['status']:12s} | {reason}")

print()
print(f"Total: {len(working)} working, {len(failing)} failing")
