"""Test all configured providers with proper API calls.

All API keys are read from environment variables. Never hardcode secrets.
"""
import os
import requests, json

def _env(name, default=""):
    return os.environ.get(name, default)

providers = [
    {
        "name": "Groq (llama 3.1 8B)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": _env("GROQ_API_KEY"),
        "payload": {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "say hi in 3 words"}], "max_tokens": 10}
    },
    {
        "name": "Groq (llama 3.3 70B)",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": _env("GROQ_API_KEY"),
        "payload": {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "say hi in 3 words"}], "max_tokens": 10}
    },
    {
        "name": "Agnes",
        "url": "https://apihub.agnes-ai.com/v1/chat/completions",
        "key": "sk-6nOFIolBFnU2YxZpdexArbYZQMA76lf7yPPn6rXlT6qgdyrO",
        "payload": {"model": "agnes-2.0-flash", "messages": [{"role": "user", "content": "say hi in 3 words"}], "max_tokens": 10}
    },
    {
        "name": "OpenCode Go",
        "url": "https://opencode.ai/zen/go/v1/chat/completions",
        "key": "sk-V1zUNkyMrsa1f865U4toV0XDySfOHIs0MO9yXSZTu8Ov0OlRIuZBzGx17cKndxIu",
        "payload": {"model": "deepseek-v4-flash", "messages": [{"role": "user", "content": "say hi in 3 words"}], "max_tokens": 10}
    },
    {
        "name": "DeepSeek Direct",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "key": "sk-e71227b2a756449aa64db61bd51a4c9e",
        "payload": {"model": "deepseek-v4-flash", "messages": [{"role": "user", "content": "say hi in 3 words"}], "max_tokens": 10}
    },
]

for p in providers:
    print(f"  {p['name']:25s}... ", end="", flush=True)
    try:
        r = requests.post(p["url"], json=p["payload"],
            headers={"Authorization": f"Bearer {p['key']}", "Content-Type": "application/json"},
            timeout=15)
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            print(f"OK ({r.elapsed.total_seconds():.1f}s): {content}")
        else:
            err = r.json().get("error", {}).get("message", r.text[:80])
            print(f"FAIL ({r.status_code}): {err}")
    except Exception as e:
        print(f"ERROR: {e}")
