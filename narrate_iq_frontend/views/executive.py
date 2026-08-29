"""
views/executive.py
-------------------
The executive landing screen. This is the single screen a busy exec
should be able to read top-to-bottom and understand the full
DATA -> INSIGHT -> EVIDENCE -> DECISION -> ACTION -> EXPERIMENT -> LEARNING
loop for the current business situation.

Data source: GET /decision (unchanged endpoint / response shape).
"""

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

from api_client import get_json, money, pct, signed_number
from components import (
    flow_step,
    hero_banner,
    kpi_tile,
    signal_kind,
    evidence_meter,
    impact_row,
    action_card,
    priority_badge,
    outcome_badge,
    badge,
    error_state,
    empty_state,
)
from theme import T


def render() -> None:
    try:
        decision = get_json("/decision")
    except requests.RequestException as exc:
        error_state(
            "Unable to load Narrate IQ decision",
            "The backend at /decision did not respond. Confirm the API is running and reachable, then refresh.",
        )
        st.code(str(exc))
        st.stop()

    kpi = decision["kpi"]
    hypothesis = decision["leading_hypothesis"]
    validation = decision["validation"]
    recommendation = decision.get("recommendation")
    experiment = decision.get("experiment")
    learning = decision.get("historical_learning")
    segments = decision.get("top_segments", [])

    # --------------------------------------------------------
    # top bar
    # --------------------------------------------------------

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.markdown('<div class="niq-eyebrow">EXECUTIVE INTELLIGENCE</div>', unsafe_allow_html=True)
        st.markdown("## Business Situation")
    with top_r:
        st.markdown(
            f"""
            <div style="text-align:right; padding-top:10px;">
                {badge("LIVE", "good", "&#9679;")}
                <div class="niq-faint" style="margin-top:6px; font-size:0.78rem;">{decision.get("date", "—")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # WHAT — hero + KPI row
    # --------------------------------------------------------

    change = float(kpi["revenue_change_pct"])
    tone = "critical" if change < 0 else ("good" if change > 0 else "neutral")
    headline = "Revenue is under pressure" if change < 0 else ("Revenue is ahead of plan" if change > 0 else "Revenue is flat")
    eyebrow = "REVENUE DETERIORATION" if change < 0 else ("REVENUE GROWTH" if change > 0 else "REVENUE MOVEMENT")

    hero_banner(
        eyebrow=eyebrow,
        title=headline,
        subtitle_html=(
            f'Revenue changed <b>{change:+.2f}%</b> week-over-week to '
            f'<b>{money(kpi["revenue"])}</b>. The sections below explain why, where it is '
            f"concentrated, what to do about it, and whether the last action worked."
        ),
        tone=tone,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_tile(
            "Revenue",
            money(kpi["revenue"]),
            delta_text=f"{change:+.2f}% WoW",
            delta_kind=signal_kind(change),
        )
    with k2:
        kpi_tile("Units Sold", f'{float(kpi["units_sold"]):,.0f}', sub="Current period")
    with k3:
        kpi_tile(
            "Confidence",
            pct(hypothesis["confidence_score"]),
            sub=hypothesis["confidence"],
        )
    with k4:
        kpi_tile(
            "Evidence Strength",
            pct(validation["validation_score"]),
            sub="Validated signal",
        )

    # --------------------------------------------------------
    # WHY — leading hypothesis + evidence
    # --------------------------------------------------------

    flow_step("02", "WHY", "Leading Hypothesis")

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            f"""
            <div class="niq-card">
                <div class="kpi-label">LEADING HYPOTHESIS</div>
                <div style="font-size:1.9rem; font-weight:800; margin-top:8px; color:var(--ink-1);">
                    {hypothesis["name"]}
                </div>
                <div style="margin-top:10px;">{badge(str(hypothesis["status"]).upper(), "accent")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        kpi_tile("Rank", f'#{hypothesis["rank"]}')

    ev1, ev2 = st.columns(2)
    with ev1:
        st.markdown('<div class="niq-card">', unsafe_allow_html=True)
        evidence_meter("Validation", validation["validation_score"])
        evidence_meter("Statistical", validation["statistical_score"])
        st.markdown("</div>", unsafe_allow_html=True)
    with ev2:
        st.markdown('<div class="niq-card">', unsafe_allow_html=True)
        evidence_meter("Segment Evidence", validation["segment_evidence_score"])
        evidence_meter("Business Context", validation["event_context_score"])
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="niq-card">
            <div class="kpi-label">SUPPORTING EVIDENCE</div>
            <div style="font-size:1rem; line-height:1.75; margin-top:10px; color:var(--ink-1);">
                {validation["supporting_evidence"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # WHERE — top segments
    # --------------------------------------------------------

    flow_step("03", "WHERE", "Concentration of Impact")

    if segments:
        left, right = st.columns([1.1, 1.9])

        with left:
            st.markdown('<div class="niq-card">', unsafe_allow_html=True)
            st.markdown('<div class="kpi-label" style="margin-bottom:6px;">BIGGEST CONTRIBUTORS</div>', unsafe_allow_html=True)
            for segment in segments[:5]:
                unit_change = float(segment["unit_change"])
                impact_row(
                    name=str(segment["value"]),
                    dimension=str(segment["dimension"]),
                    signed_value_text=signed_number(unit_change),
                    kind=signal_kind(unit_change),
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            chart_rows = [
                {"Segment": str(row["value"]), "Unit Change": float(row["unit_change"])}
                for row in segments[:10]
            ]
            chart_data = pd.DataFrame(chart_rows)
            if not chart_data.empty:
                chart_data = chart_data.sort_values("Unit Change")
                chart_data["Sign"] = chart_data["Unit Change"].apply(
                    lambda v: "Growth" if v >= 0 else "Decline"
                )
                fig = px.bar(
                    chart_data,
                    x="Unit Change",
                    y="Segment",
                    orientation="h",
                    color="Sign",
                    color_discrete_map={"Growth": T["good"], "Decline": T["critical"]},
                    text="Unit Change",
                )
                fig.update_traces(
                    texttemplate="%{text:+,.0f}",
                    textposition="outside",
                    marker_line_width=0,
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color=T["ink_2"],
                    font_family="Inter",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
                    margin=dict(l=10, r=40, t=30, b=10),
                    height=340,
                    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.18)"),
                    yaxis=dict(title=None),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        empty_state("&#128269;", "No segment breakdown available", "Segment-level contribution data was not returned for this period.")

    # --------------------------------------------------------
    # WHAT SHOULD WE DO — recommendation
    # --------------------------------------------------------

    flow_step("04", "DECISION", "What Should We Do")

    if recommendation:
        action_card(priority_badge(recommendation.get("priority")), recommendation["action"])
    else:
        empty_state("&#128161;", "No active recommendation", "Narrate IQ has not generated a recommendation for the current situation.")

    # --------------------------------------------------------
    # DID IT WORK — experiment result
    # --------------------------------------------------------

    flow_step("05", "EXPERIMENT", "Did It Work")

    if experiment:
        ex1, ex2, ex3, ex4 = st.columns(4)
        with ex1:
            kpi_tile("Status", str(experiment["status"]).upper())
        with ex2:
            kpi_tile("Target Metric", str(experiment["target_metric"]))
        with ex3:
            measured = experiment.get("measured_change_pct")
            kpi_tile(
                "Measured Change",
                f"{measured:+.2f}%" if measured is not None else "—",
                delta_kind=signal_kind(measured) if measured is not None else "neutral",
            )
        with ex4:
            st.markdown('<div class="niq-card niq-card-tight">', unsafe_allow_html=True)
            st.markdown('<div class="kpi-label">OUTCOME</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:12px;">{outcome_badge(experiment.get("outcome"))}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        empty_state("&#129514;", "No experiment in flight", "Start one from the Experiments tab to test the leading hypothesis.")

    # --------------------------------------------------------
    # WHAT DID WE LEARN — historical learning
    # --------------------------------------------------------

    flow_step("06", "LEARNING", "What Did We Learn")

    if learning:
        l1, l2, l3, l4 = st.columns(4)
        with l1:
            kpi_tile("Reliability", pct(learning["historical_reliability"]))
        with l2:
            kpi_tile("Attempts", f'{learning["attempts"]:,}')
        with l3:
            kpi_tile("Successes", f'{learning["successes"]:,}', delta_kind="good")
        with l4:
            kpi_tile("Partials", f'{learning["partials"]:,}', delta_kind="warning")
    else:
        empty_state("&#128218;", "No historical learning yet", "Reliability builds up as experiments are run and their outcomes recorded.")
