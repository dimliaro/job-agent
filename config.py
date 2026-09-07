"""
Central configuration for the job agent.
Edit the values here — everything sensitive (API keys, email password)
lives in a .env file instead (see .env.example).
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Anthropic ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# Verify the current model name at https://docs.claude.com if this ever errors.
MODEL = "claude-sonnet-5"

# --- Job source ---
# "jsearch" = live jobs via the JSearch API (needs RAPIDAPI_KEY in .env)
# "file"    = offline, read jobs_sample.json (test logic without spending quota)
SOURCE = "jsearch"

# What to search for. One API call per query (free tier = 200 calls/month).
# 6 queries once a day ≈ 180/month — near the cap, so run daily at most, or
# trim the list / run every few days if you want headroom.
# Note: no "junior" here on purpose — the scorer filters seniority, so a wider
# net catches more and the model drops the senior roles itself.
SEARCH_QUERIES = [
    "data analyst in Athens, Greece",
    "data engineer in Athens, Greece",
    "business intelligence analyst in Athens, Greece",
    "analytics engineer in Athens, Greece",
    "python developer in Athens, Greece",
    "qa automation engineer in Athens, Greece",
]
SEARCH_COUNTRY = "gr"           # ISO country code
SEARCH_DATE_POSTED = "month"    # all | today | 3days | week | month  (week is often empty for GR)
SEARCH_PAGES = 1                # 1 page ≈ up to 10 jobs per query

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# --- Scoring thresholds ---
TOP_N = 3          # how many jobs to report each run
MIN_SCORE = 60     # ignore jobs scoring below this (0-100)

# --- Your profile: this is what each job is scored against. Edit freely. ---
PROFILE = """
Entry-level / junior candidate for data roles, based in Athens (open to
hybrid/remote). Computer Science graduate (AUEB).

Core strengths:
- Python (Pandas, NumPy), SQL / SQLite, relational database design & querying
- ETL pipelines, incremental loading, automation of recurring data tasks
- Data cleaning/normalization, EDA, data-quality checks & cross-referencing
- Visualization & reporting: matplotlib, seaborn; quick to learn Power BI / Tableau
- FastAPI, Docker; some Azure, PySpark/Databricks exposure
- Also: QA automation experience (BDD, Cucumber/Gherkin) against a React app

Good fits: Data Analyst, Data Engineer, BI Analyst / BI Developer, Analytics
Engineer, ETL Developer, Data Quality / Data Management, junior Python
developer, QA automation. Bonus interest: sports / football data (has a
football-data project).

Not interested in: senior/lead roles, pure front-end roles, or unpaid internships.
"""

# --- Email (fill these in .env, not here) ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER", "")      # sender address
EMAIL_PASS = os.getenv("EMAIL_PASS", "")      # Gmail: use an App Password
EMAIL_TO = os.getenv("EMAIL_TO", "")          # where to send the digest

# --- Paths ---
MASTER_CV_PATH = "master_cv.md"
JOBS_INPUT_PATH = "jobs_sample.json"
OUTPUT_DIR = "output"
