"""
views/experiments.py
---------------------
Experiment lifecycle: proposed -> running -> completed.

Data source / mutations (unchanged):
  GET  /experiments
  POST /experiments/{id}/start    {baseline_value}
  POST /experiments/{id}/outcome  {observed_value}
"""

import requests
import streamlit as st

from api_client import get_json, post_json, refresh_data
from components import (
    experiment_stepper,
    status_badge,
    outcome_badge,
    kpi_tile,
    signal_kind,
    error_state,
    empty_state,
)


def render() -> None:
    st.markdown('<div class="niq-eyebrow">VALIDATION LOOP</div>', unsafe_allow_html=True)
    st.markdown("## Experiments")
    st.caption("Every hypothesis worth acting on gets tested before it gets trusted.")

    try:
        experiments = get_json("/experiments")
    except requests.RequestException as exc:
        error_state("Unable to load experiments", "The backend at /experiments did not respond.")
        st.code(str(exc))
        st.stop()

    if not experiments:
        empty_state("&#129514;", "No experiments yet", "Experiments are generated from ranked hypotheses on the Root Cause tab.")
        return

    for exp in experiments:
        _render_experiment_card(exp)


def _render_experiment_card(exp: dict) -> None:
    st.markdown('<div class="niq-card">', unsafe_allow_html=True)

    header_l, header_r = st.columns([3, 1])
    with header_l:
        st.markdown('<div class="kpi-label">EXPERIMENT</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:1.5rem; font-weight:800; margin-top:4px;">{exp["hypothesis"]}</div>', unsafe_allow_html=True)
    with header_r:
        st.markdown(f'<div style="text-align:right; padding-top:6px;">{status_badge(exp["status"])}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    experiment_stepper(exp["status"])

    st.markdown(f'<div class="niq-muted" style="margin-bottom:6px;">{exp["action"]}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        kpi_tile("Confidence", f"{exp['confidence_score']:.0%}")
    with c2:
        kpi_tile("Success Threshold", f"{exp['success_threshold_pct']:.1f}%")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if exp["status"] == "proposed":
        _render_proposed(exp)
    elif exp["status"] == "running":
        _render_running(exp)
    elif exp["status"] == "completed":
        _render_completed(exp)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_proposed(exp: dict) -> None:
    baseline = st.number_input(
        "Baseline value",
        min_value=0.000001,
        value=1.0,
        step=1.0,
        key=f"baseline_{exp['experiment_id']}",
    )

    if st.button("Start experiment", key=f"start_{exp['experiment_id']}", type="primary"):
        try:
            post_json(f"/experiments/{exp['experiment_id']}/start", {"baseline_value": baseline})
            refresh_data()
            st.rerun()
        except requests.RequestException as exc:
            st.error(str(exc))


def _render_running(exp: dict) -> None:
    baseline = exp.get("baseline_value")
    observed = st.number_input(
        "Observed value",
        min_value=0.000001,
        value=float(baseline if baseline is not None else 1.0),
        step=1.0,
        key=f"observed_{exp['experiment_id']}",
    )

    if st.button("Record outcome", key=f"complete_{exp['experiment_id']}", type="primary"):
        try:
            post_json(f"/experiments/{exp['experiment_id']}/outcome", {"observed_value": observed})
            refresh_data()
            st.rerun()
        except requests.RequestException as exc:
            st.error(str(exc))


def _render_completed(exp: dict) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_tile("Baseline", f'{exp["baseline_value"]}')
    with c2:
        kpi_tile("Observed", f'{exp["observed_value"]}')
    with c3:
        value = exp.get("measured_change_pct")
        kpi_tile(
            "Measured Change",
            f"{value:+.2f}%" if value is not None else "—",
            delta_kind=signal_kind(value) if value is not None else "neutral",
        )

    st.markdown(f'<div style="margin-top:12px;">{outcome_badge(exp.get("outcome"))}</div>', unsafe_allow_html=True)
