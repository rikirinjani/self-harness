"""Test Bonsai model API response time."""
import requests, json

r = requests.post(
    "http://100.83.28.83:8080/v1/chat/completions",
    json={
        "model": "/Users/ptpakdefarma/models/ternary-bonsai-27b",
        "messages": [{"role": "user", "content": "say hi in 2 words"}],
        "max_tokens": 5
    },
    timeout=30
)
print(f"Status: {r.status_code}")
print(f"Time: {r.elapsed.total_seconds():.1f}s")
if r.status_code == 200:
    print(f"Response: {r.json()['choices'][0]['message']['content']}")
else:
    print(f"Error: {r.text[:200]}")
