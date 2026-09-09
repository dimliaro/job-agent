"""
The dashboard UI. Launch with:  streamlit run dashboard.py
(or double-click dashboard.command on macOS)

Reads the jobs database the agent fills, and lets you:
  - browse jobs by run date / score / search
  - tick "applied" and write notes on any job
  - track applications and mark the response (waiting / positive / negative)

Your edits are saved back to the same database, so they survive agent re-runs.
"""

import pandas as pd
import streamlit as st

import store

st.set_page_config(page_title="Job Agent", page_icon="🧭", layout="wide")
store.init_db()

st.title("🧭 Job Agent — dashboard")

df = store.load_df()

if df.empty:
    st.info("No jobs yet. Run `python agent.py` first to populate the database.")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("Filters")
run_dates = sorted([d for d in df["run_date"].dropna().unique()], reverse=True)
picked_date = st.sidebar.selectbox("Run date", ["All"] + list(run_dates))
min_score = st.sidebar.slider("Minimum score", 0, 100, 0, step=5)
query = st.sidebar.text_input("Search title / company").strip().lower()

# Which columns the user can edit, and how they render.
COLUMN_CONFIG = {
    "score": st.column_config.NumberColumn("Score", disabled=True, width="small"),
    "title": st.column_config.TextColumn("Title", disabled=True),
    "company": st.column_config.TextColumn("Company", disabled=True),
    "location": st.column_config.TextColumn("Location", disabled=True),
    "run_date": st.column_config.TextColumn("Seen", disabled=True, width="small"),
    "url": st.column_config.LinkColumn("Link", display_text="open", disabled=True),
    "reasons": st.column_config.TextColumn("Why", disabled=True),
    "cv_path": st.column_config.TextColumn("CV file", disabled=True),
    "applied": st.column_config.CheckboxColumn("Applied?"),
    "response": st.column_config.SelectboxColumn(
        "Response", options=["none", "waiting", "positive", "negative"]
    ),
    "notes": st.column_config.TextColumn("Notes", width="large"),
}
SHOW_COLS = ["score", "title", "company", "location", "run_date", "url",
             "reasons", "applied", "response", "notes", "cv_path", "id"]


def editor(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    """Render an editable table; 'id' is hidden but carried for saving."""
    return st.data_editor(
        frame[SHOW_COLS],
        column_config={**COLUMN_CONFIG, "id": None},   # None hides the column
        hide_index=True,
        use_container_width=True,
        key=key,
    )


tab_all, tab_applied = st.tabs(
    ["All jobs", f"Applications ({int(df['applied'].sum())})"]
)

with tab_all:
    view = df.copy()
    if picked_date != "All":
        view = view[view["run_date"] == picked_date]
    view = view[view["score"] >= min_score]
    if query:
        mask = (view["title"].str.lower().str.contains(query)
                | view["company"].str.lower().str.contains(query))
        view = view[mask]

    st.caption(f"{len(view)} jobs shown. Edit Applied / Response / Notes, then save.")
    edited = editor(view, key="all")
    if st.button("💾 Save changes", key="save_all"):
        store.save_edits(edited)
        st.success("Saved.")
        st.rerun()

with tab_applied:
    applied = df[df["applied"] == 1]
    if applied.empty:
        st.info("Nothing marked as applied yet. Tick 'Applied?' on a job in the first tab.")
    else:
        st.caption("Jobs you've applied to. Set the response as you hear back.")
        edited_applied = editor(applied, key="applied")
        if st.button("💾 Save changes", key="save_applied"):
            store.save_edits(edited_applied)
            st.success("Saved.")
            st.rerun()
