#!/bin/bash
# Double-click this on macOS to open the dashboard in your browser.
cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || true
exec streamlit run dashboard.py
