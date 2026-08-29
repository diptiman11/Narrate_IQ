"""
views/data.py
--------------
Dataset status, upload, a quick local quality check, and the button
that runs the real Narrate IQ intelligence pipeline.

Nothing about the pipeline itself changed: same module list, same
subprocess execution, same stop-on-first-failure behavior, same
required file (data/raw/sales.csv). The additions here are purely
frontend UX: an actual file uploader (the original only *checked* for
files, it never let you provide them), a quick client-side quality
score shown before the real backend validation runs, and a per-module
progress indicator instead of a single opaque spinner.
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from api_client import refresh_data
from components import flow_step, badge
from data_quality import quick_quality_score, score_band

RAW_DIR = Path("data/raw")

# filename -> (display name, required for the pipeline to run)
DATASETS = {
    "sales.csv": ("Sales", True),
    "inventory.csv": ("Inventory", False),
    "marketing.csv": ("Marketing", False),
    "business_events.csv": ("Events", False),
}

# Pipeline modules, run in order, unchanged from the original app.
PIPELINE_MODULES = [
    "src.kpi.engine",
    "src.anomaly.engine",
    "src.drivers.engine",
    "src.attribution.engine",
    "src.confidence.engine",
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


def render() -> None:
    st.markdown('<div class="niq-eyebrow">DATA</div>', unsafe_allow_html=True)
    st.markdown("## Data")
    st.caption("Manage the active business datasets used by Narrate IQ.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    flow_step("01", "STATUS", "Active Datasets")
    _render_status_tiles()

    flow_step("02", "UPLOAD", "Replace or Add a Dataset")
    _render_upload_area()

    flow_step("03", "RUN", "Narrate IQ Analysis")
    _render_run_pipeline()


# ============================================================
# status tiles
# ============================================================

def _render_status_tiles() -> None:
    cols = st.columns(len(DATASETS))
    for col, (filename, (label, required)) in zip(cols, DATASETS.items()):
        exists = (RAW_DIR / filename).exists()
        with col:
            if exists:
                status_html = badge("READY", "good", "&#9679;")
            elif required:
                status_html = badge("REQUIRED — MISSING", "critical", "&#9679;")
            else:
                status_html = badge("OPTIONAL", "neutral", "&#9679;")
            st.markdown(
                f"""
                <div class="niq-card niq-card-tight">
                    <div class="kpi-label">{label}</div>
                    <div style="margin-top:10px;">{status_html}</div>
                    <div class="niq-faint" style="margin-top:8px; font-size:0.74rem;">{filename}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# upload + quick quality check + lightweight column preview
# ============================================================

def _render_upload_area() -> None:
    st.markdown('<div class="niq-card">', unsafe_allow_html=True)

    target_filename = st.selectbox(
        "Dataset to replace",
        options=list(DATASETS.keys()),
        format_func=lambda f: f"{DATASETS[f][0]}  ·  {f}",
    )

    uploaded = st.file_uploader(
        f"Upload {DATASETS[target_filename][0]} CSV",
        type=["csv"],
        key=f"uploader_{target_filename}",
    )

    if uploaded is not None:
        try:
            preview_df = pd.read_csv(uploaded)
        except Exception as exc:  # noqa: BLE001 - surfaced to the user as-is
            st.error(f"Could not read this file as CSV: {exc}")
        else:
            quality = quick_quality_score(preview_df)
            band = score_band(quality["score"])

            q1, q2, q3, q4 = st.columns(4)
            with q1:
                st.markdown(
                    f'<div class="kpi-label">QUALITY SCORE</div>'
                    f'<div class="kpi-value" style="font-size:1.5rem;">{quality["score"]}/100</div>'
                    f'<div style="margin-top:6px;">{badge(band.upper(), band)}</div>',
                    unsafe_allow_html=True,
                )
            with q2:
                st.markdown(f'<div class="kpi-label">ROWS</div><div class="kpi-value" style="font-size:1.5rem;">{quality["rows"]:,}</div>', unsafe_allow_html=True)
            with q3:
                st.markdown(f'<div class="kpi-label">MISSING</div><div class="kpi-value" style="font-size:1.5rem;">{quality["missing_pct"]}%</div>', unsafe_allow_html=True)
            with q4:
                st.markdown(f'<div class="kpi-label">DUPLICATE ROWS</div><div class="kpi-value" style="font-size:1.5rem;">{quality["duplicate_pct"]}%</div>', unsafe_allow_html=True)

            st.caption(
                "This is a quick local check shown before the file reaches Narrate IQ's real "
                "ingestion and validation pipeline — it is not a substitute for it."
            )

            with st.expander("Preview detected columns"):
                st.dataframe(
                    pd.DataFrame({"column": preview_df.columns, "dtype": [str(t) for t in preview_df.dtypes]}),
                    use_container_width=True,
                    hide_index=True,
                )
                st.dataframe(preview_df.head(10), use_container_width=True, hide_index=True)

            if st.button(f"Save as data/raw/{target_filename}", type="primary"):
                uploaded.seek(0)
                (RAW_DIR / target_filename).write_bytes(uploaded.getvalue())
                refresh_data()
                st.success(f"Saved {target_filename}. It is now the active dataset for its slot.")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# run pipeline (unchanged subprocess logic, restyled progress)
# ============================================================

def _render_run_pipeline() -> None:
    st.markdown(
        """
        <div class="niq-card">
            <div class="kpi-label">RECOMMENDED WORKFLOW</div>
            <div class="niq-muted" style="margin-top:10px; line-height:1.9;">
                1&#41; Upload &nbsp;&middot;&nbsp; 2&#41; Preview &amp; check quality &nbsp;&middot;&nbsp;
                3&#41; Save &nbsp;&middot;&nbsp; 4&#41; Run Narrate IQ Analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Run Narrate IQ Analysis", type="primary", use_container_width=True):
        sales_exists = (RAW_DIR / "sales.csv").exists()

        if not sales_exists:
            st.error("Sales data is required.")
            return

        progress = st.progress(0.0, text="Starting pipeline...")
        logs = []
        success = True

        for i, module in enumerate(PIPELINE_MODULES):
            progress.progress(i / len(PIPELINE_MODULES), text=f"Running {module}...")

            process = subprocess.run(
                [sys.executable, "-m", module],
                capture_output=True,
                text=True,
            )
            logs.append(f"--- {module} ---\n{process.stdout}{process.stderr}")

            if process.returncode != 0:
                success = False
                break

        progress.progress(1.0, text="Done")

        if success:
            refresh_data()
            st.session_state.page = "Executive"
            st.success("Pipeline completed. Loading the Executive view...")
            st.rerun()
        else:
            st.error("Pipeline failed.")
            with st.expander("Pipeline logs", expanded=True):
                st.code("\n\n".join(logs))
