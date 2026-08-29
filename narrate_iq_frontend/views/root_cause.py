"""
views/root_cause.py
--------------------
Interactive drill-down: ranked hypotheses, then a filterable
contribution explorer by dimension (region / product / channel / etc).

Data source: GET /root-cause (unchanged endpoint / response shape:
a flat "graph" list of nodes tagged node_type = "hypothesis" | "segment").
"""

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

from api_client import get_json
from components import flow_step, error_state, empty_state
from theme import T


def render() -> None:
    st.markdown('<div class="niq-eyebrow">DIAGNOSTIC</div>', unsafe_allow_html=True)
    st.markdown("## Root Cause")
    st.caption("Every ranked hypothesis and the evidence graph behind it.")

    try:
        data = get_json("/root-cause")
    except requests.RequestException as exc:
        error_state("Unable to load root-cause data", "The backend at /root-cause did not respond.")
        st.code(str(exc))
        st.stop()

    graph = data.get("graph", [])
    hypotheses = [row for row in graph if row.get("node_type") == "hypothesis"]
    segments = [row for row in graph if row.get("node_type") == "segment"]

    # --------------------------------------------------------
    # ranked hypotheses
    # --------------------------------------------------------

    flow_step("01", "HYPOTHESES", "Ranked by Confidence")

    if hypotheses:
        df = pd.DataFrame(
            [
                {
                    "Rank": int(row["rank"]),
                    "Hypothesis": row["node"],
                    "Confidence": float(row["confidence_score"]),
                    "Validation": float(row["validation_score"]),
                    "Status": row["status"],
                }
                for row in hypotheses
            ]
        ).sort_values("Rank")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
                "Confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1, format="%.0f%%"),
                "Validation": st.column_config.ProgressColumn("Validation", min_value=0, max_value=1, format="%.0f%%"),
                "Status": st.column_config.TextColumn("Status"),
            },
        )
    else:
        empty_state("&#128269;", "No hypotheses returned", "The root-cause graph did not include any hypothesis nodes.")

    # --------------------------------------------------------
    # contribution explorer
    # --------------------------------------------------------

    flow_step("02", "EVIDENCE", "Contribution Explorer")

    if not segments:
        empty_state("&#128202;", "No segment evidence available")
        return

    dimensions = sorted({row["dimension"] for row in segments})
    dimension = st.selectbox("Dimension", dimensions)

    filtered = sorted(
        [row for row in segments if row["dimension"] == dimension],
        key=lambda row: row["unit_change"],
    )

    chart_df = pd.DataFrame(
        [
            {
                "Segment": row["dimension_value"],
                "Unit Change": float(row["unit_change"]),
                "Sign": "Growth" if float(row["unit_change"]) >= 0 else "Decline",
            }
            for row in filtered
        ]
    )

    if not chart_df.empty:
        fig = px.bar(
            chart_df,
            x="Unit Change",
            y="Segment",
            orientation="h",
            color="Sign",
            color_discrete_map={"Growth": T["good"], "Decline": T["critical"]},
            text="Unit Change",
        )
        fig.update_traces(texttemplate="%{text:+,.0f}", textposition="outside", marker_line_width=0)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=T["ink_2"],
            font_family="Inter",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
            margin=dict(l=10, r=40, t=30, b=10),
            height=440,
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.18)"),
            yaxis=dict(title=None),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    detail_df = pd.DataFrame(
        [
            {
                "Segment": row["dimension_value"],
                "Unit Change": row["unit_change"],
                "Change %": row["unit_change_pct"],
                "Contribution %": row["contribution_share_pct"],
            }
            for row in filtered
        ]
    )

    st.dataframe(
        detail_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Unit Change": st.column_config.NumberColumn("Unit Change", format="%+,.0f"),
            "Change %": st.column_config.NumberColumn("Change %", format="%+.2f%%"),
            "Contribution %": st.column_config.NumberColumn("Contribution %", format="%.1f%%"),
        },
    )
