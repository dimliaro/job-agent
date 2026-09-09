"""
Persistence layer: a small SQLite database that remembers every job the agent
has scored, plus your own annotations (applied? response? notes).

Design rule that matters: when the agent re-runs and sees a job again, it
updates only the *machine* fields (score, reasons, dates, cv_path). It never
touches your fields (applied / response / notes), so your edits survive re-runs.
"""

import sqlite3
from contextlib import contextmanager

import pandas as pd

import config


@contextmanager
def _conn():
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id          TEXT PRIMARY KEY,
                first_seen  TEXT,
                last_seen   TEXT,
                run_date    TEXT,
                title       TEXT,
                company     TEXT,
                location    TEXT,
                url         TEXT,
                score       INTEGER,
                reasons     TEXT,
                cv_path     TEXT,
                applied     INTEGER DEFAULT 0,          -- 0/1, your field
                response    TEXT    DEFAULT 'none',     -- none|waiting|positive|negative, your field
                notes       TEXT    DEFAULT ''          -- your field
            )
            """
        )


def upsert_job(job: dict, run_date: str) -> None:
    """Insert a newly seen job, or refresh the machine fields of an existing one.
    `job` needs: id, title, company, location, url, score, reasons."""
    with _conn() as con:
        exists = con.execute("SELECT 1 FROM jobs WHERE id = ?", (job["id"],)).fetchone()
        if exists:
            con.execute(
                """UPDATE jobs SET last_seen=?, run_date=?, title=?, company=?,
                       location=?, url=?, score=?, reasons=?
                   WHERE id=?""",
                (run_date, run_date, job["title"], job["company"], job["location"],
                 job["url"], job["score"], job["reasons"], job["id"]),
            )
        else:
            con.execute(
                """INSERT INTO jobs
                       (id, first_seen, last_seen, run_date, title, company,
                        location, url, score, reasons)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (job["id"], run_date, run_date, run_date, job["title"], job["company"],
                 job["location"], job["url"], job["score"], job["reasons"]),
            )


def set_cv(job_id: str, cv_path: str) -> None:
    with _conn() as con:
        con.execute("UPDATE jobs SET cv_path=? WHERE id=?", (cv_path, job_id))


def load_df() -> pd.DataFrame:
    with _conn() as con:
        return pd.read_sql_query(
            "SELECT * FROM jobs ORDER BY score DESC, last_seen DESC", con
        )


def save_edits(df: pd.DataFrame) -> None:
    """Write back the user-editable fields (applied / response / notes)."""
    with _conn() as con:
        for _, r in df.iterrows():
            con.execute(
                "UPDATE jobs SET applied=?, response=?, notes=? WHERE id=?",
                (int(bool(r["applied"])), r["response"] or "none", r["notes"] or "", r["id"]),
            )
