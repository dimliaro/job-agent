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

# What to search for lives in TRACKS below (one query list per track).
# One API call per query (free tier = 200 calls/month). 6 queries in total once
# a day ≈ 180/month — near the cap, so keep the total across tracks at ~6, or
# run every few days if you want more queries.
# Note: no "junior" in the queries on purpose — the scorer filters seniority, so
# a wider net catches more and the model drops the senior roles itself.
SEARCH_COUNTRY = "gr"           # ISO country code
SEARCH_DATE_POSTED = "all"      # all | today | 3days | week | month — GR jobs have no post date in JSearch, so any filter returns 0
SEARCH_PAGES = 1                # 1 page ≈ up to 10 jobs per query

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# --- Scoring thresholds (applied per track) ---
TOP_N = 3          # how many jobs to report per track each run
MIN_SCORE = 60     # ignore jobs scoring below this (0-100)

# --- Your profiles: each job is scored against its track's profile. Edit freely. ---
PROFILE_DATA = """
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

PROFILE_IT = """
Entry-level / junior candidate for IT support roles, based in Kifisia, Athens.
Computer Science graduate (AUEB, 2025).

Core strengths:
- Hardware: PC assembly, upgrades (RAM, SSD/NVMe), cleaning/repasting,
  component diagnosis; desktops, laptops, MacBooks, printers, peripherals
- Windows installs/reinstalls, BIOS/UEFI, drivers; Active Directory (users,
  password resets, security groups); basic Linux
- Networking: routers, Wi-Fi troubleshooting, IP configuration on wired LANs,
  Ethernet cabling
- IT support during military service (Research & Informatics Corps): AD admin,
  PC upgrades, IT asset inventory
- 3 years customer-facing retail at an electronics store, assisting the
  in-store technician; some Python/SQL scripting

Good fits: Helpdesk / Service Desk, IT Support Technician, Desktop Support,
Field / On-site Technician, PC / Hardware Technician, junior System or
Network Administrator.

Not interested in: senior/lead roles, pure sales roles, or unpaid internships.
"""

# --- Tracks: each one is searched, scored and reported separately. ---
# Every track has its own queries, its own profile and its own master CV,
# and gets its own section in the email digest.
TRACKS = [
    {
        "name": "data",
        "label": "Data roles",
        "queries": [
            "data analyst in Athens, Greece",
            "data engineer in Athens, Greece",
            "business intelligence analyst in Athens, Greece",
        ],
        "profile": PROFILE_DATA,
        "cv_path": "master_cv.md",
    },
    {
        "name": "it",
        "label": "IT support roles",
        "queries": [
            "IT support in Athens, Greece",
            "helpdesk technician in Athens, Greece",
            "system administrator in Athens, Greece",
        ],
        "profile": PROFILE_IT,
        "cv_path": "master_cv_it.md",
    },
]

# --- Email (fill these in .env, not here) ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER", "")      # sender address
EMAIL_PASS = os.getenv("EMAIL_PASS", "")      # Gmail: use an App Password
EMAIL_TO = os.getenv("EMAIL_TO", "")          # where to send the digest

# --- Paths ---
JOBS_INPUT_PATH = "jobs_sample.json"
OUTPUT_DIR = "output"
DB_PATH = "jobs.db"       # SQLite database powering the dashboard
