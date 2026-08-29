"""
app.py
------
Narrate IQ frontend entry point.

This file only does routing and shell chrome (sidebar, navigation,
page dispatch). All business logic, API calls, and formatting live in
api_client.py; all presentation primitives live in components.py and
theme.py; each screen's layout lives in views/*.py.

Run with:  streamlit run app.py
Backend:   unchanged FastAPI service at API_URL (see api_client.py)
"""

import streamlit as st

from api_client import refresh_data
from theme import inject_theme
from views import copilot, data, experiments, learning, root_cause, executive

try:
    from streamlit_option_menu import option_menu
except ImportError:
    st.set_page_config(page_title="Narrate IQ", layout="wide")
    st.error(
        "Missing dependency **streamlit-option-menu**.\n\n"
        "Install it with:\n\n```\npip install streamlit-option-menu\n```\n\n"
        "then rerun the app. See the README for why this dependency was added."
    )
    st.stop()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Narrate IQ",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Executive"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ============================================================
# NAVIGATION
# ============================================================

PAGES = ["Executive", "Root Cause", "Experiments", "Learning", "Data", "AI Copilot"]
ICONS = ["speedometer2", "search", "flask", "graph-up-arrow", "database", "chat-dots"]

with st.sidebar:
    st.markdown('<div class="niq-brand">◉ NARRATE IQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="niq-brand-sub">Decision Intelligence Terminal</div>', unsafe_allow_html=True)

    selection = option_menu(
        menu_title=None,
        options=PAGES,
        icons=ICONS,
        default_index=PAGES.index(st.session_state.page),
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#98A2B5", "font-size": "15px"},
            "nav-link": {
                "font-family": "Inter, sans-serif",
                "font-size": "14px",
                "font-weight": "600",
                "color": "#98A2B5",
                "border-radius": "10px",
                "margin": "2px 0",
                "padding": "10px 12px",
                "--hover-color": "#171B24",
            },
            "nav-link-selected": {
                "background-color": "rgba(91,141,239,0.14)",
                "color": "#F4F6FA",
                "font-weight": "700",
            },
        },
    )
    st.session_state.page = selection

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if st.button("&#8635; Refresh data", use_container_width=True):
        refresh_data()
        st.rerun()

    st.markdown(
        """
        <div style="margin-top:26px; padding-top:16px; border-top:1px solid var(--border-subtle);
                    color:var(--ink-3); font-size:0.72rem; line-height:1.9; font-family:var(--font-data);">
            INTELLIGENCE ENGINE&nbsp;&nbsp;<span style="color:var(--good);">&#9679;</span><br>
            EVIDENCE GRAPH&nbsp;&nbsp;<span style="color:var(--good);">&#9679;</span><br>
            EXPERIMENT LOOP&nbsp;&nbsp;<span style="color:var(--good);">&#9679;</span><br>
            HISTORICAL LEARNING&nbsp;&nbsp;<span style="color:var(--good);">&#9679;</span><br>
            GROQ COPILOT&nbsp;&nbsp;<span style="color:var(--good);">&#9679;</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ROUTE
# ============================================================

ROUTES = {
    "Executive": executive.render,
    "Root Cause": root_cause.render,
    "Experiments": experiments.render,
    "Learning": learning.render,
    "Data": data.render,
    "AI Copilot": copilot.render,
}

ROUTES[st.session_state.page]()
