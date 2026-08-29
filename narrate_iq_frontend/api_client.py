"""
api_client.py
--------------
All backend I/O and value formatting for Narrate IQ.

This is a straight extraction of the original app's networking and
formatting functions - endpoints, payloads, cache TTL, and formatting
rules are unchanged. Nothing about the intelligence engine or the API
contract was touched.
"""

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"


# ============================================================
# API (unchanged endpoints / behavior)
# ============================================================

@st.cache_data(ttl=20)
def get_json(endpoint: str):
    response = requests.get(f"{API_URL}{endpoint}", timeout=30)
    response.raise_for_status()
    return response.json()


def post_json(endpoint: str, payload: dict):
    response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def refresh_data():
    st.cache_data.clear()


# ============================================================
# FORMAT (unchanged rules)
# ============================================================

def money(value):
    if value is None:
        return "—"
    return f"${float(value):,.0f}"


def pct(value):
    if value is None:
        return "—"
    return f"{float(value) * 100:.0f}%"


def signed_pct(value):
    if value is None:
        return "—"
    return f"{float(value):+.2f}%"


def signed_number(value):
    if value is None:
        return "—"
    return f"{float(value):+,.0f}"
