"""
One-off diagnostic: fire a single JSearch query and print the raw response
structure, so we can see exactly what the API returns. Uses 1 API call.
Run:  python debug_jsearch.py
"""

import json
import requests
import config

QUERY = "data analyst in Athens, Greece"

headers = {
    "X-RapidAPI-Key": config.RAPIDAPI_KEY,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}
params = {
    "query": QUERY,
    "country": config.SEARCH_COUNTRY,
    "date_posted": "month",   # widen the window for the test
    "num_pages": "1",
}

resp = requests.get("https://jsearch.p.rapidapi.com/search-v2",
                    headers=headers, params=params, timeout=30)

print("HTTP status:", resp.status_code)
try:
    payload = resp.json()
except Exception:
    print("Body (not JSON):", resp.text[:1000])
    raise

print("Top-level keys:", list(payload.keys()))

data = payload.get("data")
print("type(data):", type(data).__name__)
if isinstance(data, dict):
    print("data keys:", list(data.keys()))
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  data[{k!r}] is a list of {len(v)}")

# Try to show the first job object, wherever it is.
def first_job(p):
    d = p.get("data")
    if isinstance(d, list) and d:
        return d[0]
    if isinstance(d, dict):
        for key in ("jobs", "results", "data", "items"):
            if isinstance(d.get(key), list) and d[key]:
                return d[key][0]
    return None

job = first_job(payload)
if job:
    print("\nFirst job keys:", list(job.keys()))
    slim = {k: (str(v)[:80] + "…" if isinstance(v, str) and len(v) > 80 else v)
            for k, v in job.items()}
    print(json.dumps(slim, ensure_ascii=False, indent=2)[:1500])
else:
    print("\nNo job objects found. Full payload (truncated):")
    print(json.dumps(payload, ensure_ascii=False, indent=2)[:1500])
