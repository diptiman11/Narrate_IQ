from pathlib import Path
import subprocess
import sys

import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

def ask_chatbot(
    question: str,
    conversation: list[dict[str, str]],
) -> str:

    response = requests.post(
        f"{API_URL}/chat",
        json={
            "question": question,
            "conversation": conversation,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()["answer"]


# ============================================================
# CONFIG
# ============================================================


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"


st.set_page_config(
    page_title="Narrate IQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "Executive"


# ============================================================
# API HELPERS
# ============================================================

@st.cache_data(ttl=30)
def api_get(endpoint: str):
    response = requests.get(
        f"{API_URL}{endpoint}",
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


def api_post(
    endpoint: str,
    payload: dict,
):
    response = requests.post(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=20,
    )

    response.raise_for_status()

    return response.json()


def refresh_data():
    st.cache_data.clear()


# ============================================================
# FORMAT HELPERS
# ============================================================

def pct(value, decimals=0):
    if value is None:
        return "—"

    return f"{float(value) * 100:.{decimals}f}%"


def raw_pct(value, decimals=2):
    if value is None:
        return "—"

    return f"{float(value):.{decimals}f}%"


def money(value):
    if value is None:
        return "—"

    return f"${float(value):,.0f}"


def number(value):
    if value is None:
        return "—"

    return f"{float(value):,.0f}"


# ============================================================
# PIPELINE
# ============================================================

PIPELINE_MODULES = [
    "src.drilldown.sales",
    "src.context.events",
    "src.evidence.validator",
    "src.learning.history",
    "src.learning.engine",
    "src.hypotheses.engine",
    "src.recommendations.engine",
    "src.rootcause.engine",
    "src.experiments.engine",
    "src.decision.engine",
    "src.llm.narrative",
]


def run_pipeline():

    logs = []

    for module in PIPELINE_MODULES:

        process = subprocess.run(
            [
                sys.executable,
                "-m",
                module,
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        output = (
            process.stdout
            + "\n"
            + process.stderr
        ).strip()

        logs.append(
            f"=== {module} ===\n{output}"
        )

        if process.returncode != 0:
            logs.append(
                f"\nPipeline stopped at {module}."
            )

            return False, logs

    return True, logs


# ============================================================
# DATA UPLOAD
# ============================================================

SCHEMAS = {
    "Sales": [
        "date",
        "product_id",
        "region",
        "channel",
        "units",
        "revenue",
    ],
    "Inventory": [
        "date",
        "product_id",
        "region",
        "warehouse",
        "units_sold",
        "closing_stock",
        "stockout_hours",
    ],
    "Marketing": [
        "date",
        "region",
        "impressions",
        "clicks",
        "spend",
        "conversions",
    ],
    "Business Events": [
        "event_date",
        "event_name",
        "event_type",
        "description",
    ],
}


ALIASES = {
    "date": [
        "date",
        "transaction_date",
        "order_date",
        "day",
    ],
    "product_id": [
        "product_id",
        "product",
        "sku",
        "item_id",
    ],
    "region": [
        "region",
        "geo",
        "location",
        "area",
    ],
    "channel": [
        "channel",
        "sales_channel",
        "platform",
    ],
    "units": [
        "units",
        "quantity",
        "qty",
        "units_sold",
    ],
    "revenue": [
        "revenue",
        "sales",
        "net_sales",
        "sales_value",
        "amount",
    ],
    "warehouse": [
        "warehouse",
        "warehouse_id",
        "location_id",
    ],
    "closing_stock": [
        "closing_stock",
        "ending_stock",
        "stock",
        "inventory",
    ],
    "stockout_hours": [
        "stockout_hours",
        "out_of_stock_hours",
        "stockout",
    ],
    "impressions": [
        "impressions",
        "views",
        "ad_impressions",
    ],
    "clicks": [
        "clicks",
        "ad_clicks",
    ],
    "spend": [
        "spend",
        "marketing_spend",
        "ad_spend",
        "cost",
    ],
    "conversions": [
        "conversions",
        "conversion",
        "orders",
    ],
    "event_date": [
        "event_date",
        "date",
        "event_day",
    ],
    "event_name": [
        "event_name",
        "event",
        "name",
    ],
    "event_type": [
        "event_type",
        "type",
        "category",
    ],
    "description": [
        "description",
        "details",
        "notes",
        "comment",
    ],
}


def normalize_name(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def suggest_column(
    target,
    columns,
):

    normalized = {
        normalize_name(column): column
        for column in columns
    }

    for alias in ALIASES.get(
        target,
        [target],
    ):

        alias = normalize_name(alias)

        if alias in normalized:
            return normalized[alias]

    return None


def quality_report(df):

    total_cells = (
        len(df) * len(df.columns)
    )

    missing = int(
        df.isna().sum().sum()
    )

    duplicates = int(
        df.duplicated().sum()
    )

    invalid_dates = 0

    for column in df.columns:

        if "date" in column.lower():

            parsed = pd.to_datetime(
                df[column],
                errors="coerce",
            )

            invalid_dates += int(
                parsed.isna().sum()
            )

    missing_pct = (
        missing / total_cells * 100
        if total_cells
        else 0
    )

    duplicate_pct = (
        duplicates / len(df) * 100
        if len(df)
        else 0
    )

    score = 100

    score -= min(
        missing_pct * 2,
        20,
    )

    score -= min(
        duplicate_pct * 2,
        15,
    )

    score -= min(
        invalid_dates
        / max(len(df), 1)
        * 100,
        15,
    )

    score = max(
        0,
        min(score, 100),
    )

    return {
        "rows": len(df),
        "missing_pct": missing_pct,
        "duplicate_pct": duplicate_pct,
        "invalid_dates": invalid_dates,
        "score": score,
    }


def render_upload(
    label,
    filename,
    schema,
):

    st.markdown(
        f"### {label}"
    )

    uploaded = st.file_uploader(
        f"Upload {label} CSV",
        type=["csv"],
        key=f"upload_{label}",
    )

    if uploaded is None:
        return

    try:

        df = pd.read_csv(
            uploaded
        )

    except Exception as exc:

        st.error(
            f"Unable to read file: {exc}"
        )

        return

    st.success(
        f"{len(df):,} rows loaded."
    )

    st.markdown(
        "#### Column Mapping"
    )

    columns = [
        None,
        *list(df.columns),
    ]

    mapping = {}

    for target in schema:

        suggestion = suggest_column(
            target,
            list(df.columns),
        )

        default_index = (
            columns.index(
                suggestion
            )
            if suggestion in columns
            else 0
        )

        mapping[target] = st.selectbox(
            target,
            columns,
            index=default_index,
            key=f"map_{label}_{target}",
        )

    missing = [
        target
        for target, source in mapping.items()
        if source is None
    ]

    rename_map = {
        source: target
        for target, source in mapping.items()
        if source is not None
    }

    normalized = df.rename(
        columns=rename_map
    ).copy()

    st.markdown(
        "#### Data Quality"
    )

    quality = quality_report(
        normalized
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Rows",
            f"{quality['rows']:,}",
        )

    with c2:
        st.metric(
            "Missing",
            f"{quality['missing_pct']:.2f}%",
        )

    with c3:
        st.metric(
            "Duplicates",
            f"{quality['duplicate_pct']:.2f}%",
        )

    with c4:
        st.metric(
            "Quality",
            f"{quality['score']:.0f}/100",
        )

    if quality["score"] >= 60:
        st.success(
            "Dataset passes the quality threshold."
        )
    else:
        st.error(
            "Dataset quality is too low."
        )

    st.markdown(
        "#### Preview"
    )

    st.dataframe(
        normalized.head(5),
        use_container_width=True,
        hide_index=True,
    )

    if st.button(
        f"Save {filename}",
        key=f"save_{label}",
        type="primary",
        use_container_width=True,
    ):

        if missing:

            st.error(
                "Map all required fields."
            )

            return

        if quality["score"] < 60:

            st.error(
                "Improve data quality before saving."
            )

            return

        RAW_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        normalized.to_csv(
            RAW_DIR / filename,
            index=False,
        )

        st.success(
            f"{filename} saved successfully."
        )

        st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🧠 Narrate IQ"
)

st.sidebar.caption(
    "Decision Intelligence Platform"
)

st.sidebar.divider()

pages = [
    "Executive",
    "Root Cause",
    "Experiments",
    "Learning",
    "Data",
    "Chat",
]

st.session_state.page = st.sidebar.radio(
    "Navigate",
    pages,
    index=pages.index(
        st.session_state.page
    ),
)

st.sidebar.divider()

if st.sidebar.button(
    "🔄 Refresh",
    use_container_width=True,
):

    refresh_data()
    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🧠 Narrate IQ"
)

st.caption(
    "Detect → Explain → Locate → Recommend → Experiment → Learn"
)


# ============================================================
# EXECUTIVE
# ============================================================

if st.session_state.page == "Executive":

    try:

        decision = api_get(
            "/decision"
        )

    except requests.RequestException as exc:

        st.error(
            "Unable to load decision data."
        )

        st.code(
            str(exc)
        )

        st.stop()

    kpi = decision["kpi"]
    hypothesis = decision[
        "leading_hypothesis"
    ]
    validation = decision[
        "validation"
    ]

    recommendation = decision.get(
        "recommendation"
    )

    experiment = decision.get(
        "experiment"
    )

    learning = decision.get(
        "historical_learning"
    )

    # --------------------------------------------------------
    # Business situation
    # --------------------------------------------------------

    revenue_change = float(
        kpi["revenue_change_pct"]
    )

    if revenue_change < 0:

        st.error(
            f"⚠ Revenue deterioration "
            f"{revenue_change:.2f}% WoW"
        )

    else:

        st.success(
            f"Revenue changed "
            f"{revenue_change:.2f}% WoW"
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Revenue",
            money(
                kpi["revenue"]
            ),
            f"{revenue_change:.2f}% WoW",
        )

    with c2:
        st.metric(
            "Units Sold",
            number(
                kpi["units_sold"]
            ),
        )

    with c3:
        st.metric(
            "Confidence",
            pct(
                hypothesis[
                    "confidence_score"
                ]
            ),
        )

    with c4:
        st.metric(
            "Validation",
            pct(
                validation[
                    "validation_score"
                ]
            ),
        )

    st.divider()

    # --------------------------------------------------------
    # Leading hypothesis
    # --------------------------------------------------------

    st.subheader(
        "🎯 Leading Hypothesis"
    )

    h1, h2, h3 = st.columns(
        [4, 1, 1]
    )

    with h1:

        st.markdown(
            f"### {hypothesis['name']}"
        )

        st.write(
            f"Status: **{hypothesis['status']}**"
        )

    with h2:

        st.metric(
            "Rank",
            f"#{hypothesis['rank']}",
        )

    with h3:

        st.metric(
            "Confidence",
            pct(
                hypothesis[
                    "confidence_score"
                ]
            ),
        )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    st.subheader(
        "Why?"
    )

    e1, e2, e3, e4 = st.columns(4)

    with e1:
        st.metric(
            "Overall",
            pct(
                validation[
                    "validation_score"
                ]
            ),
        )

    with e2:
        st.metric(
            "Statistical",
            pct(
                validation[
                    "statistical_score"
                ]
            ),
        )

    with e3:
        st.metric(
            "Segments",
            pct(
                validation[
                    "segment_evidence_score"
                ]
            ),
        )

    with e4:
        st.metric(
            "Context",
            pct(
                validation[
                    "event_context_score"
                ]
            ),
        )

    st.info(
        validation[
            "supporting_evidence"
        ]
    )

    # --------------------------------------------------------
    # Impact
    # --------------------------------------------------------

    st.subheader(
        "📍 Biggest Impact Areas"
    )

    segments = decision.get(
        "top_segments",
        [],
    )

    if segments:

        segment_df = pd.DataFrame(
            segments
        )

        segment_df = segment_df[
            [
                "dimension",
                "value",
                "unit_change",
                "unit_change_pct",
                "contribution_share_pct",
            ]
        ]

        segment_df.columns = [
            "Dimension",
            "Segment",
            "Unit Change",
            "Change %",
            "Contribution %",
        ]

        st.dataframe(
            segment_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No segment evidence available."
        )

    # --------------------------------------------------------
    # Action / Experiment
    # --------------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.subheader(
            "🚀 Recommended Action"
        )

        if recommendation:

            st.markdown(
                f"**Priority:** "
                f"`{recommendation['priority'].upper()}`"
            )

            st.success(
                recommendation["action"]
            )

        else:

            st.info(
                "No recommendation available."
            )

    with right:

        st.subheader(
            "🧪 Experiment"
        )

        if experiment:

            c1, c2 = st.columns(2)

            with c1:

                st.metric(
                    "Status",
                    experiment[
                        "status"
                    ].upper(),
                )

            with c2:

                st.metric(
                    "Outcome",
                    (
                        experiment[
                            "outcome"
                        ].upper()
                        if experiment[
                            "outcome"
                        ]
                        else "—"
                    ),
                )

            if experiment.get(
                "measured_change_pct"
            ) is not None:

                st.write(
                    "Measured change: "
                    f"**{experiment['measured_change_pct']:.2f}%**"
                )

        else:

            st.info(
                "No experiment available."
            )

    # --------------------------------------------------------
    # Learning
    # --------------------------------------------------------

    st.subheader(
        "🧠 Historical Learning"
    )

    if learning:

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Reliability",
                pct(
                    learning[
                        "historical_reliability"
                    ]
                ),
            )

        with c2:
            st.metric(
                "Attempts",
                learning[
                    "attempts"
                ],
            )

        with c3:
            st.metric(
                "Successes",
                learning[
                    "successes"
                ],
            )

        with c4:
            st.metric(
                "Partials",
                learning[
                    "partials"
                ],
            )

    else:

        st.info(
            "No historical learning yet."
        )


# ============================================================
# ROOT CAUSE
# ============================================================

elif st.session_state.page == "Root Cause":

    st.subheader(
        "🔎 Root Cause Explorer"
    )

    try:

        data = api_get(
            "/root-cause"
        )

    except requests.RequestException as exc:

        st.error(
            str(exc)
        )

        st.stop()

    graph = data.get(
        "graph",
        [],
    )

    hypotheses = [
        row
        for row in graph
        if row.get(
            "node_type"
        ) == "hypothesis"
    ]

    segments = [
        row
        for row in graph
        if row.get(
            "node_type"
        ) == "segment"
    ]

    if hypotheses:

        st.markdown(
            "### Hypothesis Ranking"
        )

        st.dataframe(
            [
                {
                    "Rank": int(
                        row["rank"]
                    ),
                    "Hypothesis": row[
                        "node"
                    ],
                    "Confidence": pct(
                        row[
                            "confidence_score"
                        ]
                    ),
                    "Validation": pct(
                        row[
                            "validation_score"
                        ]
                    ),
                    "Status": row[
                        "status"
                    ],
                }
                for row in hypotheses
            ],
            use_container_width=True,
            hide_index=True,
        )

    if segments:

        st.markdown(
            "### Segment Analysis"
        )

        dimensions = sorted(
            {
                row["dimension"]
                for row in segments
            }
        )

        dimension = st.selectbox(
            "Dimension",
            dimensions,
        )

        filtered = [
            row
            for row in segments
            if row["dimension"]
            == dimension
        ]

        filtered = sorted(
            filtered,
            key=lambda row: row[
                "unit_change"
            ],
        )

        chart_df = pd.DataFrame(
            {
                str(
                    row["dimension_value"]
                ): float(
                    row["unit_change"]
                )
                for row in filtered
            },
            index=["Unit Change"],
        ).T

        st.bar_chart(
            chart_df
        )

        st.dataframe(
            [
                {
                    "Segment": row[
                        "dimension_value"
                    ],
                    "Unit Change": row[
                        "unit_change"
                    ],
                    "Change %": row[
                        "unit_change_pct"
                    ],
                    "Contribution %": row[
                        "contribution_share_pct"
                    ],
                }
                for row in filtered
            ],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# EXPERIMENTS
# ============================================================

elif st.session_state.page == "Experiments":

    st.subheader(
        "🧪 Experiment Control Center"
    )

    try:

        experiments = api_get(
            "/experiments"
        )

    except requests.RequestException as exc:

        st.error(
            str(exc)
        )

        st.stop()

    if not experiments:

        st.info(
            "No experiments available."
        )

    for exp in experiments:

        with st.expander(
            (
                f"{exp['hypothesis']} · "
                f"{exp['status'].upper()}"
            ),
            expanded=(
                exp["status"]
                == "running"
            ),
        ):

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Confidence",
                    f"{exp['confidence_score']:.0%}",
                )

            with c2:
                st.metric(
                    "Target",
                    exp["target_metric"],
                )

            with c3:
                st.metric(
                    "Threshold",
                    f"{exp['success_threshold_pct']:.1f}%",
                )

            st.write(
                exp["action"]
            )

            if exp["status"] == "proposed":

                baseline = st.number_input(
                    "Baseline value",
                    min_value=0.000001,
                    value=1.0,
                    step=1.0,
                    key=f"baseline_{exp['experiment_id']}",
                )

                if st.button(
                    "▶ Start Experiment",
                    key=f"start_{exp['experiment_id']}",
                    type="primary",
                ):

                    try:

                        api_post(
                            (
                                f"/experiments/"
                                f"{exp['experiment_id']}"
                                "/start"
                            ),
                            {
                                "baseline_value": baseline
                            },
                        )

                        st.success(
                            "Experiment started."
                        )

                        refresh_data()
                        st.rerun()

                    except requests.RequestException as exc:

                        st.error(
                            str(exc)
                        )

            elif exp["status"] == "running":

                baseline = exp.get(
                    "baseline_value"
                )

                st.info(
                    f"Baseline: {baseline}"
                )

                observed = st.number_input(
                    "Observed value",
                    min_value=0.000001,
                    value=float(
                        baseline
                        if baseline is not None
                        else 1.0
                    ),
                    step=1.0,
                    key=f"observed_{exp['experiment_id']}",
                )

                if st.button(
                    "✅ Complete Experiment",
                    key=f"complete_{exp['experiment_id']}",
                    type="primary",
                ):

                    try:

                        result = api_post(
                            (
                                f"/experiments/"
                                f"{exp['experiment_id']}"
                                "/outcome"
                            ),
                            {
                                "observed_value": observed
                            },
                        )

                        outcome = result.get(
                            "outcome"
                        )

                        change = result.get(
                            "measured_change_pct"
                        )

                        if outcome == "success":

                            st.success(
                                "🎉 Experiment succeeded."
                            )

                        elif outcome == "partial":

                            st.warning(
                                "🟡 Experiment partially succeeded."
                            )

                        else:

                            st.error(
                                "❌ Experiment failed."
                            )

                        if change is not None:

                            st.write(
                                f"Measured change: "
                                f"**{change:.2f}%**"
                            )

                        refresh_data()
                        st.rerun()

                    except requests.RequestException as exc:

                        st.error(
                            str(exc)
                        )

            elif exp["status"] == "completed":

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Baseline",
                        exp.get(
                            "baseline_value"
                        ),
                    )

                with c2:
                    st.metric(
                        "Observed",
                        exp.get(
                            "observed_value"
                        ),
                    )

                with c3:

                    change = exp.get(
                        "measured_change_pct"
                    )

                    st.metric(
                        "Change",
                        (
                            f"{change:.2f}%"
                            if change is not None
                            else "—"
                        ),
                    )

                outcome = exp.get(
                    "outcome"
                )

                if outcome == "success":
                    st.success(
                        "🎉 SUCCESS"
                    )

                elif outcome == "partial":
                    st.warning(
                        "🟡 PARTIAL"
                    )

                elif outcome == "failed":
                    st.error(
                        "❌ FAILED"
                    )


# ============================================================
# LEARNING
# ============================================================

elif st.session_state.page == "Learning":

    st.subheader(
        "📈 Hypothesis Learning"
    )

    try:

        learning = api_get(
            "/learning"
        )

    except requests.RequestException as exc:

        st.error(
            str(exc)
        )

        st.stop()

    summary = learning.get(
        "summary",
        [],
    )

    history = learning.get(
        "history",
        [],
    )

    if summary:

        st.markdown(
            "### Historical Reliability"
        )

        summary_df = pd.DataFrame(
            summary
        )

        if "historical_reliability" in summary_df.columns:
            summary_df[
                "historical_reliability"
            ] = (
                summary_df[
                    "historical_reliability"
                ]
                * 100
            )

        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No learning summary yet."
        )

    st.divider()

    st.markdown(
        "### Experiment History"
    )

    if history:

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No completed experiment history."
        )


# ============================================================
# DATA
# ============================================================
elif st.session_state.page == "Chat":

    st.header(
        "💬 Ask Narrate IQ"
    )

    st.caption(
        "Your evidence-grounded business intelligence copilot."
    )

    st.info(
        "Ask questions about the current Narrate IQ "
        "business analysis. Answers are grounded in "
        "the current decision and evidence."
    )

    # ========================================================
    # CHAT STATE
    # ========================================================

    if "chat_messages" not in st.session_state:

        st.session_state.chat_messages = []

    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.button(
        "🗑️ Clear conversation",
        use_container_width=True,
    ):

        st.session_state.chat_messages = []

        st.rerun()

    st.divider()

    # ========================================================
    # SUGGESTED QUESTIONS
    # ========================================================

    st.subheader(
        "Suggested questions"
    )

    q1, q2, q3 = st.columns(3)

    selected_question = None

    with q1:

        if st.button(
            "Why did revenue decline?",
            use_container_width=True,
        ):

            selected_question = (
                "Why did revenue decline?"
            )

    with q2:

        if st.button(
            "Where is the biggest impact?",
            use_container_width=True,
        ):

            selected_question = (
                "Where is the biggest impact?"
            )

    with q3:

        if st.button(
            "Did the experiment work?",
            use_container_width=True,
        ):

            selected_question = (
                "Did the experiment work?"
            )

    # ========================================================
    # PROCESS SUGGESTED QUESTION
    # ========================================================

    if selected_question:

        conversation = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message
            in st.session_state.chat_messages
        ]

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": selected_question,
            }
        )

        try:

            with st.spinner(
                "Narrate IQ is analyzing the evidence..."
            ):

                answer = ask_chatbot(
                    selected_question,
                    conversation,
                )

            st.session_state.chat_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

        except requests.RequestException as exc:

            st.error(
                f"Chat request failed: {exc}"
            )

        st.rerun()

    # ========================================================
    # DISPLAY CHAT HISTORY
    # ========================================================

    for message in st.session_state.chat_messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # ========================================================
    # FREE-FORM CHAT
    # ========================================================

    question = st.chat_input(
        "Ask about revenue, root cause, segments, "
        "recommendations, experiments, or learning..."
    )

    if question:

        conversation = [
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message
            in st.session_state.chat_messages
        ]

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Narrate IQ is analyzing the evidence..."
            ):

                try:

                    answer = ask_chatbot(
                        question,
                        conversation,
                    )

                    st.markdown(
                        answer
                    )

                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except requests.RequestException as exc:

                    st.error(
                        f"Unable to contact Narrate IQ: {exc}"
                    )
# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Narrate IQ • Evidence-backed business intelligence"
)