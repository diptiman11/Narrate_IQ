from pathlib import Path

import pandas as pd
import streamlit as st

from frontend.pipeline import run_pipeline


RAW_DIR = Path("data/raw")


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


def normalize_name(name: str) -> str:
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def suggest_column(
    target: str,
    columns: list[str],
) -> str | None:

    normalized = {
        normalize_name(column): column
        for column in columns
    }

    aliases = ALIASES.get(
        target,
        [target],
    )

    for alias in aliases:

        alias = normalize_name(alias)

        if alias in normalized:
            return normalized[alias]

    return None


def suggest_mapping(
    columns: list[str],
    required_columns: list[str],
) -> dict[str, str | None]:

    return {
        target: suggest_column(
            target,
            columns,
        )
        for target in required_columns
    }


def normalize_dataframe(
    df: pd.DataFrame,
    mapping: dict[str, str | None],
) -> pd.DataFrame:

    rename_map = {
        source: target
        for target, source in mapping.items()
        if source is not None
    }

    return df.rename(
        columns=rename_map
    ).copy()


# ============================================================
# DATA QUALITY
# ============================================================

def calculate_quality(
    df: pd.DataFrame,
) -> dict:

    total_cells = (
        len(df) * len(df.columns)
    )

    missing_cells = int(
        df.isna().sum().sum()
    )

    missing_pct = (
        missing_cells
        / total_cells
        * 100
        if total_cells
        else 0.0
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    duplicate_pct = (
        duplicate_rows
        / len(df)
        * 100
        if len(df)
        else 0.0
    )

    invalid_dates = 0

    date_columns = [
        column
        for column in df.columns
        if "date" in column.lower()
    ]

    for column in date_columns:

        parsed = pd.to_datetime(
            df[column],
            errors="coerce",
        )

        invalid_dates += int(
            parsed.isna().sum()
        )

    negative_numeric_cells = 0

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        negative_numeric_cells += int(
            (df[column] < 0).sum()
        )

    score = 100.0

    score -= min(
        missing_pct * 2,
        20,
    )

    score -= min(
        duplicate_pct * 2,
        15,
    )

    if date_columns:

        score -= min(
            (
                invalid_dates
                / max(len(df), 1)
                * 100
            ),
            15,
        )

    score -= min(
        (
            negative_numeric_cells
            / max(total_cells, 1)
            * 100
        ),
        10,
    )

    score = max(
        0.0,
        min(score, 100.0),
    )

    if score >= 90:
        status = "excellent"
    elif score >= 75:
        status = "good"
    elif score >= 60:
        status = "warning"
    else:
        status = "poor"

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": duplicate_pct,
        "invalid_dates": invalid_dates,
        "negative_numeric_cells": negative_numeric_cells,
        "quality_score": score,
        "status": status,
    }


def render_quality_report(
    df: pd.DataFrame,
) -> bool:

    quality = calculate_quality(df)

    st.markdown("#### Data Quality")

    c1, c2, c3, c4, c5 = st.columns(5)

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
            "Invalid Dates",
            quality["invalid_dates"],
        )

    with c5:
        st.metric(
            "Quality Score",
            f"{quality['quality_score']:.0f}/100",
        )

    if quality["status"] == "excellent":
        st.success("Data quality is excellent.")

    elif quality["status"] == "good":
        st.success("Data quality is good.")

    elif quality["status"] == "warning":
        st.warning("Data quality needs review.")

    else:
        st.error("Data quality is poor.")

    return quality["quality_score"] >= 60


# ============================================================
# UPLOAD + MAPPING
# ============================================================

def render_upload(
    label: str,
    filename: str,
    required_columns: list[str],
    key: str,
) -> None:

    st.markdown(
        f"### {label}"
    )

    uploaded_file = st.file_uploader(
        f"Upload {label} CSV",
        type=["csv"],
        key=f"upload_{key}",
    )

    if uploaded_file is None:
        return

    try:
        df = pd.read_csv(
            uploaded_file
        )

    except Exception as exc:

        st.error(
            f"Could not read CSV: {exc}"
        )
        return

    if df.empty:

        st.error(
            "Uploaded file contains no rows."
        )
        return

    st.success(
        f"Loaded {len(df):,} rows and "
        f"{len(df.columns)} columns."
    )

    # --------------------------------------------------------
    # Mapping
    # --------------------------------------------------------

    suggested = suggest_mapping(
        list(df.columns),
        required_columns,
    )

    st.markdown(
        "#### Column Mapping"
    )

    mapping = {}

    columns = [
        None,
        *list(df.columns),
    ]

    for target in required_columns:

        suggestion = suggested.get(
            target
        )

        default_index = (
            columns.index(
                suggestion
            )
            if suggestion in columns
            else 0
        )

        mapping[target] = st.selectbox(
            f"`{target}`",
            columns,
            index=default_index,
            key=f"{key}_{target}",
        )

    missing = [
        target
        for target, source in mapping.items()
        if source is None
    ]

    if missing:

        st.warning(
            "Unmapped fields: "
            + ", ".join(missing)
        )

    normalized = normalize_dataframe(
        df,
        mapping,
    )

    # --------------------------------------------------------
    # Quality
    # --------------------------------------------------------

    quality_ready = render_quality_report(
        normalized
    )

    # --------------------------------------------------------
    # Preview
    # --------------------------------------------------------

    st.markdown(
        "#### Normalized Preview"
    )

    st.dataframe(
        normalized.head(5),
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    if st.button(
        f"Save normalized {filename}",
        key=f"save_{key}",
        type="primary",
        use_container_width=True,
    ):

        if missing:

            st.error(
                "Map all required fields before saving."
            )
            return

        if not quality_ready:

            st.error(
                "Data quality is too low to continue."
            )
            return

        RAW_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            RAW_DIR / filename
        )

        normalized.to_csv(
            output_path,
            index=False,
        )

        st.success(
            f"Saved normalized {filename}."
        )


# ============================================================
# MAIN INGESTION PAGE
# ============================================================

def render_ingestion():

    st.header(
        "📥 Data Ingestion"
    )

    st.write(
        "Upload business data, validate it, "
        "and run Narrate IQ."
    )

    # ========================================================
    # CURRENT DATA STATUS
    # ========================================================

    sales_exists = (
        RAW_DIR / "sales.csv"
    ).exists()

    inventory_exists = (
        RAW_DIR / "inventory.csv"
    ).exists()

    marketing_exists = (
        RAW_DIR / "marketing.csv"
    ).exists()

    events_exists = (
        RAW_DIR / "business_events.csv"
    ).exists()

    st.subheader(
        "📊 Current Data Status"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Sales",
            "✅ Ready"
            if sales_exists
            else "❌ Required",
        )

    with c2:
        st.metric(
            "Inventory",
            "✅ Ready"
            if inventory_exists
            else "Optional",
        )

    with c3:
        st.metric(
            "Marketing",
            "✅ Ready"
            if marketing_exists
            else "Optional",
        )

    with c4:
        st.metric(
            "Business Events",
            "✅ Ready"
            if events_exists
            else "Optional",
        )

    st.divider()

    # ========================================================
    # RUN ANALYSIS
    # ========================================================

    st.subheader(
        "🚀 Run Narrate IQ"
    )

    if sales_exists:

        st.success(
            "Sales data is ready. "
            "You can run the analysis now."
        )

    else:

        st.warning(
            "Sales data is required before "
            "running the analysis."
        )

    if st.button(
        "🚀 Run Narrate IQ Analysis",
        type="primary",
        use_container_width=True,
        disabled=not sales_exists,
    ):

        with st.spinner(
            "Running Narrate IQ intelligence pipeline..."
        ):

            success, logs = run_pipeline()

        if success:

            st.success(
                "✅ Analysis completed successfully."
            )

            st.cache_data.clear()

            st.info(
                "Analysis updated. "
                "Open the Executive tab."
            )

        else:

            st.error(
                "❌ Analysis pipeline failed."
            )

            with st.expander(
                "Pipeline logs",
                expanded=True,
            ):

                for log in logs:
                    st.code(log)

    st.divider()

    # ========================================================
    # UPLOADS
    # ========================================================

    st.subheader(
        "📤 Upload and Prepare Data"
    )

    st.caption(
        "Sales is required. Inventory, Marketing, "
        "and Business Events are optional enrichments."
    )

    # Sales
    render_upload(
        label="🛒 Sales",
        filename="sales.csv",
        required_columns=SCHEMAS["Sales"],
        key="sales",
    )

    st.divider()

    # Inventory
    render_upload(
        label="📦 Inventory",
        filename="inventory.csv",
        required_columns=SCHEMAS["Inventory"],
        key="inventory",
    )

    st.divider()

    # Marketing
    render_upload(
        label="📣 Marketing",
        filename="marketing.csv",
        required_columns=SCHEMAS["Marketing"],
        key="marketing",
    )

    st.divider()

    # Business Events
    render_upload(
        label="🌐 Business Events",
        filename="business_events.csv",
        required_columns=SCHEMAS["Business Events"],
        key="events",
    )