"""
Where jobs come from.

Two sources, chosen by config.SOURCE:
  "jsearch"  -> live jobs via the JSearch API (Google for Jobs aggregator).
                Covers the Greek market (kariera.gr, skywalker.gr, LinkedIn,
                Indeed, ...). Needs a free RapidAPI key in .env (RAPIDAPI_KEY).
  "file"     -> read jobs_sample.json. Offline, burns no API calls — use it
                for testing the scoring/CV logic without spending your quota.

Legality: JSearch is an official API product, so this is not scraping. Do NOT
add a source that scrapes LinkedIn/Instagram directly — that breaks their ToS.

Every source returns a list of dicts with the same shape:
  {id, title, company, location, url, description}
"""

import json
import time
from typing import List, Dict

import requests

import config

JSEARCH_URL = "https://jsearch.p.rapidapi.com/search-v2"
JSEARCH_TIMEOUT = 45     # seconds to wait for a response
JSEARCH_RETRIES = 3      # attempts before giving up on a query


def load_jobs(path: str) -> List[Dict]:
    """Offline source: read jobs from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _clean(s):
    """Drop lone/broken surrogate chars (e.g. half-emoji) that break JSON encoding."""
    if not isinstance(s, str):
        return s
    return s.encode("utf-8", "ignore").decode("utf-8", "ignore")


def _map_jsearch(item: dict) -> Dict:
    """Map one JSearch result into our common job shape."""
    if not isinstance(item, dict):
        return {}
    city = item.get("job_city") or ""
    country = item.get("job_country") or ""
    location = item.get("job_location") or ", ".join(p for p in (city, country) if p) or "N/A"
    if item.get("job_is_remote"):
        location = f"{location} (Remote)" if location != "N/A" else "Remote"
    return {
        "id": item.get("job_id", ""),
        "title": _clean(item.get("job_title", "")),
        "company": _clean(item.get("employer_name", "")) or "N/A",
        "location": _clean(location),
        "url": item.get("job_apply_link", ""),
        "description": _clean(item.get("job_description") or "")[:4000],  # keep prompts lean
    }


def _extract_jobs(payload: dict) -> List[dict]:
    """Find the list of job objects in a JSearch response, wherever it lives.
    search-v2 nests them (e.g. data.jobs) alongside a cursor; older /search put
    them directly in data. Handle both, and surface the shape if we can't."""
    data = payload.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("jobs", "results", "data", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    for key in ("jobs", "results", "items"):
        if isinstance(payload.get(key), list):
            return payload[key]
    # Couldn't locate it — show the structure so we can fix the mapping fast.
    top = list(payload.keys())
    inner = list(data.keys()) if isinstance(data, dict) else type(data).__name__
    raise RuntimeError(
        f"Couldn't find the jobs list in the JSearch response. "
        f"Top-level keys: {top}. data: {inner}"
    )


def fetch_from_jsearch(query: str) -> List[Dict]:
    """One JSearch search call -> list of jobs. Uses 1 request of your quota."""
    if not config.RAPIDAPI_KEY:
        raise RuntimeError("RAPIDAPI_KEY is empty — put your key in .env, or set SOURCE='file'.")

    headers = {
        "X-RapidAPI-Key": config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    # search-v2 uses cursor-based paging, so no "page" param — num_pages still works.
    params = {
        "query": query,
        "country": config.SEARCH_COUNTRY,
        "date_posted": config.SEARCH_DATE_POSTED,
        "num_pages": str(config.SEARCH_PAGES),
    }

    # Retry on slow/flaky responses: a single timeout shouldn't lose the query.
    resp = None
    for attempt in range(1, JSEARCH_RETRIES + 1):
        try:
            resp = requests.get(JSEARCH_URL, headers=headers, params=params,
                                timeout=JSEARCH_TIMEOUT)
            break
        except requests.exceptions.RequestException as e:
            if attempt == JSEARCH_RETRIES:
                raise
            wait = 2 ** attempt   # 2s, 4s, ...
            print(f"    JSearch attempt {attempt} failed ({e.__class__.__name__}); "
                  f"retrying in {wait}s…")
            time.sleep(wait)

    if resp.status_code in (401, 403):
        raise RuntimeError(
            "JSearch rejected the key (HTTP "
            f"{resp.status_code}). Check that your RAPIDAPI_KEY is correct and "
            "that you've subscribed to the JSearch API (free Basic plan) on RapidAPI."
        )
    if resp.status_code == 429:
        raise RuntimeError("JSearch rate limit hit (HTTP 429) — you've used up your quota for now.")
    resp.raise_for_status()

    jobs = _extract_jobs(resp.json())
    return [mapped for item in jobs if (mapped := _map_jsearch(item))]


def get_jobs() -> List[Dict]:
    """Dispatcher: pull jobs from whichever source config.SOURCE selects."""
    if config.SOURCE == "file":
        return load_jobs(config.JOBS_INPUT_PATH)

    if config.SOURCE == "jsearch":
        seen, jobs = set(), []
        failures = 0
        for query in config.SEARCH_QUERIES:          # one API call per query
            try:
                results = fetch_from_jsearch(query)
            except requests.exceptions.RequestException as e:
                failures += 1
                print(f"  ! query failed after retries, skipping: {query!r} ({e.__class__.__name__})")
                continue
            for job in results:
                if job["id"] and job["id"] not in seen:
                    seen.add(job["id"])
                    jobs.append(job)
        # Only give up entirely if every query failed (network/API down).
        if failures == len(config.SEARCH_QUERIES) and failures > 0:
            raise RuntimeError("All JSearch queries failed — the API or network looks down right now.")
        return jobs

    raise ValueError(f"Unknown SOURCE: {config.SOURCE!r} (use 'jsearch' or 'file').")


# --- Stub for later, if you want to add company career-page feeds ---

def fetch_from_rss(feed_url: str) -> List[Dict]:
    """Parse an RSS/Atom career feed into job dicts. (requires: feedparser)"""
    raise NotImplementedError("Plug in a real career-page RSS feed here.")