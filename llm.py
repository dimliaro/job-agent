"""
The two LLM calls that do the real work:
  - score_job:  how well does this job fit the profile? (0-100 + reasons)
  - tailor_cv:  rewrite the master CV, targeted at one job

Both use the Anthropic Python SDK. Keep prompts here so they're easy to tune.
"""

import json
from anthropic import Anthropic
import config

client = Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _text(message) -> str:
    """Pull the plain text out of a Messages API response."""
    return "".join(block.text for block in message.content if block.type == "text")


def score_job(job: dict, profile: str) -> dict:
    """Return {'score': int, 'verdict': 'keep'|'skip', 'reasons': str}."""
    prompt = f"""You are screening a job for a candidate.

CANDIDATE PROFILE:
{profile}

JOB:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job['description']}

Score how well this job fits the candidate from 0 to 100, where 100 is a
perfect match and 0 is completely irrelevant. Consider seniority, role type,
required skills, and location. Then decide 'keep' or 'skip'.

Respond with ONLY a JSON object, no markdown, no extra text:
{{"score": <int>, "verdict": "keep" or "skip", "reasons": "<one sentence>"}}"""

    msg = client.messages.create(
        model=config.MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = _text(msg).strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fail safe: if parsing breaks, keep the job for manual review.
        return {"score": 50, "verdict": "keep", "reasons": f"Could not parse LLM output: {raw[:120]}"}


def tailor_cv(master_cv: str, job: dict) -> str:
    """Return a CV (markdown) rewritten to target this specific job."""
    prompt = f"""You are a CV editor. Rewrite the candidate's master CV so it is
targeted at the job below. Rules:
- Only use facts already present in the master CV. Do NOT invent experience.
- Reorder and reword bullets to surface what's most relevant to this job.
- Rewrite the summary/objective to speak to this role.
- Keep it truthful and concise. Output clean Markdown only.

JOB:
Title: {job['title']} at {job['company']}
Description: {job['description']}

MASTER CV:
{master_cv}"""

    msg = client.messages.create(
        model=config.MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return _text(msg).strip()
