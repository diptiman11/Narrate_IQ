"""
views/learning.py
------------------
The feedback loop: which hypotheses have proven reliable over time,
and the full experiment history behind that judgment.

Data source: GET /learning (unchanged: {"summary": [...], "history": [...]})
"""

import requests
import streamlit as st

from api_client import get_json
from components import flow_step, error_state, empty_state


def render() -> None:
    st.markdown('<div class="niq-eyebrow">FEEDBACK LOOP</div>', unsafe_allow_html=True)
    st.markdown("## Learning")
    st.caption("Narrate IQ gets more trustworthy the more it's used — this is the record of that.")

    try:
        data = get_json("/learning")
    except requests.RequestException as exc:
        error_state("Unable to load learning data", "The backend at /learning did not respond.")
        st.code(str(exc))
        st.stop()

    summary = data.get("summary", [])
    history = data.get("history", [])

    flow_step("01", "RELIABILITY", "Hypothesis Track Record")

    if summary:
        column_config = {}
        sample_row = summary[0]
        for key in sample_row.keys():
            lowered = key.lower()
            if "reliab" in lowered or ("rate" in lowered and isinstance(sample_row[key], (int, float)) and abs(sample_row[key]) <= 1):
                column_config[key] = st.column_config.ProgressColumn(key.replace("_", " ").title(), min_value=0, max_value=1, format="%.0f%%")

        st.dataframe(summary, use_container_width=True, hide_index=True, column_config=column_config)
    else:
        empty_state("&#128200;", "No reliability data yet", "This fills in once experiments start completing.")

    flow_step("02", "HISTORY", "Every Experiment Run")

    if history:
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        empty_state("&#128220;", "No experiment history yet")
