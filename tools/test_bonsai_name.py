"""Test Bonsai with short model name vs full path."""
import requests, json

base = "http://100.83.28.83:8080/v1"
msg = [{"role": "user", "content": "say hi in 2 words"}]

# Test with short name
print("Testing short name 'ternary-bonsai-27b'...")
r = requests.post(f"{base}/chat/completions",
    json={"model": "ternary-bonsai-27b", "messages": msg, "max_tokens": 5},
    timeout=10)
print(f"  Status: {r.status_code} ({r.elapsed.total_seconds():.1f}s)")
if r.status_code == 200:
    print(f"  Response: {r.json()['choices'][0]['message']['content']}")
else:
    print(f"  Error: {r.text[:100]}")

# Test with full path
print("\nTesting full path '/Users/ptpakdefarma/models/ternary-bonsai-27b'...")
r = requests.post(f"{base}/chat/completions",
    json={"model": "/Users/ptpakdefarma/models/ternary-bonsai-27b", "messages": msg, "max_tokens": 5},
    timeout=10)
print(f"  Status: {r.status_code} ({r.elapsed.total_seconds():.1f}s)")
if r.status_code == 200:
    print(f"  Response: {r.json()['choices'][0]['message']['content']}")
else:
    print(f"  Error: {r.text[:100]}")
