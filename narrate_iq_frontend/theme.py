"""
theme.py
--------
Design tokens and global CSS injection for the Narrate IQ terminal.

Nothing here touches data, business logic, or API calls. It only
controls how the app looks. Change values in TOKENS to retheme the
whole product from one place.
"""

import streamlit as st

# ============================================================
# DESIGN TOKENS
# ============================================================
# Semantic rule enforced everywhere in this app:
#   - green  -> positive / success / favorable business signal
#   - red    -> negative / failed / unfavorable business signal
#   - amber  -> partial / warning / needs attention (not failure)
#   - blue   -> interactive / informational accent (never a business signal)
#   - gray   -> neutral / structural information
#
# Color is never the only carrier of meaning: every status chip and
# delta pairs its color with an icon and/or text label.

TOKENS = {
    # surfaces
    "bg_page": "#0A0C11",
    "bg_glow_1": "rgba(91, 141, 239, 0.10)",
    "bg_glow_2": "rgba(239, 68, 68, 0.05)",
    "surface_1": "#12151C",
    "surface_2": "#171B24",
    "surface_3": "#1D222C",
    "border_subtle": "rgba(255,255,255,0.07)",
    "border_strong": "rgba(255,255,255,0.16)",
    # ink
    "ink_1": "#F4F6FA",
    "ink_2": "#98A2B5",
    "ink_3": "#656D7E",
    # accent (interactive only, never a business signal)
    "accent": "#5B8DEF",
    "accent_soft": "rgba(91,141,239,0.14)",
    "accent_strong": "#82AAFF",
    # semantic / status (fixed meaning, never reused for anything else)
    "good": "#22C55E",
    "good_soft": "rgba(34,197,94,0.14)",
    "warning": "#F5A623",
    "warning_soft": "rgba(245,166,35,0.14)",
    "critical": "#EF4444",
    "critical_soft": "rgba(239,68,68,0.14)",
    "serious": "#F0725A",
    "serious_soft": "rgba(240,114,90,0.14)",
    "neutral": "#98A2B5",
    "neutral_soft": "rgba(152,162,181,0.14)",
}

T = TOKENS  # short alias used throughout this module


def inject_theme() -> None:
    """Inject fonts, CSS variables, and component styles. Call once per run."""

    st.markdown(
        f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {{
    --bg-page: {T["bg_page"]};
    --surface-1: {T["surface_1"]};
    --surface-2: {T["surface_2"]};
    --surface-3: {T["surface_3"]};
    --border-subtle: {T["border_subtle"]};
    --border-strong: {T["border_strong"]};
    --ink-1: {T["ink_1"]};
    --ink-2: {T["ink_2"]};
    --ink-3: {T["ink_3"]};
    --accent: {T["accent"]};
    --accent-soft: {T["accent_soft"]};
    --accent-strong: {T["accent_strong"]};
    --good: {T["good"]};
    --good-soft: {T["good_soft"]};
    --warning: {T["warning"]};
    --warning-soft: {T["warning_soft"]};
    --critical: {T["critical"]};
    --critical-soft: {T["critical_soft"]};
    --serious: {T["serious"]};
    --serious-soft: {T["serious_soft"]};
    --neutral: {T["neutral"]};
    --neutral-soft: {T["neutral_soft"]};
    --font-ui: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    --font-data: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 18px;
}}

html, body, [class*="css"] {{ font-family: var(--font-ui); }}

/* ---------- app canvas ---------- */

.stApp {{
    background:
        radial-gradient(circle at 82% -6%, {T["bg_glow_1"]}, transparent 32%),
        radial-gradient(circle at 4% 90%, {T["bg_glow_2"]}, transparent 28%),
        linear-gradient(180deg, var(--bg-page) 0%, #0D1015 100%);
    color: var(--ink-1);
}}

.block-container {{
    max-width: 1480px;
    padding-top: 1.4rem;
    padding-bottom: 4rem;
}}

::selection {{ background: var(--accent-soft); }}

a, a:visited {{ color: var(--accent-strong); }}

hr {{ border-color: var(--border-subtle); }}

/* ---------- sidebar ---------- */

section[data-testid="stSidebar"] {{
    background: #0B0D12;
    border-right: 1px solid var(--border-subtle);
}}
section[data-testid="stSidebar"] * {{ color: var(--ink-2); }}
section[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}

/* ---------- typography ---------- */

h1, h2, h3 {{ color: var(--ink-1) !important; letter-spacing: -0.02em; font-weight: 800; }}
p, label, span {{ color: inherit; }}
.niq-muted {{ color: var(--ink-2); }}
.niq-faint {{ color: var(--ink-3); }}

/* ---------- structural: eyebrow / section flow labels ---------- */

.niq-eyebrow {{
    font-family: var(--font-data);
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-3);
}}

.niq-flow-step {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 34px 0 14px;
}}
.niq-flow-step .flow-index {{
    font-family: var(--font-data);
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--bg-page);
    background: var(--accent);
    border-radius: 5px;
    padding: 2px 7px;
    letter-spacing: 0.04em;
}}
.niq-flow-step .flow-label {{
    font-family: var(--font-data);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-2);
}}
.niq-flow-step .flow-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--ink-1);
    margin-left: 4px;
}}

/* ---------- generic surfaces / cards ---------- */

.niq-card {{
    background: linear-gradient(150deg, var(--surface-2), var(--surface-1));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 22px 24px;
    box-shadow: 0 12px 30px -14px rgba(0,0,0,0.55);
    margin-bottom: 16px;
    transition: border-color 120ms ease;
}}
.niq-card:hover {{ border-color: var(--border-strong); }}
.niq-card-tight {{ padding: 16px 18px; }}

/* ---------- KPI tiles ---------- */

.kpi-label {{
    font-family: var(--font-data);
    color: var(--ink-3);
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
.kpi-value {{
    font-family: var(--font-data);
    color: var(--ink-1);
    font-size: 2rem;
    font-weight: 700;
    margin-top: 8px;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.01em;
}}
.kpi-sub {{ margin-top: 6px; font-size: 0.82rem; color: var(--ink-2); }}

/* ---------- delta / signed values (color + glyph, never color alone) ---------- */

.delta {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: var(--font-data);
    font-weight: 700;
    font-size: 0.86rem;
    font-variant-numeric: tabular-nums;
}}
.delta-good {{ color: var(--good); }}
.delta-critical {{ color: var(--critical); }}
.delta-neutral {{ color: var(--ink-2); }}

/* ---------- badges / pills (status: color + label, never color alone) ---------- */

.niq-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-family: var(--font-data);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border: 1px solid transparent;
    white-space: nowrap;
}}
.niq-badge-good {{ background: var(--good-soft); color: var(--good); border-color: rgba(34,197,94,0.35); }}
.niq-badge-critical {{ background: var(--critical-soft); color: var(--critical); border-color: rgba(239,68,68,0.35); }}
.niq-badge-warning {{ background: var(--warning-soft); color: var(--warning); border-color: rgba(245,166,35,0.35); }}
.niq-badge-serious {{ background: var(--serious-soft); color: var(--serious); border-color: rgba(240,114,90,0.35); }}
.niq-badge-accent {{ background: var(--accent-soft); color: var(--accent-strong); border-color: rgba(91,141,239,0.35); }}
.niq-badge-neutral {{ background: var(--neutral-soft); color: var(--ink-2); border-color: var(--border-subtle); }}

/* ---------- hero / situation banner ---------- */

.niq-hero {{
    border-radius: 22px;
    padding: 32px 34px;
    margin-bottom: 22px;
    border: 1px solid var(--border-subtle);
    position: relative;
    overflow: hidden;
}}
.niq-hero-critical {{
    background: linear-gradient(135deg, rgba(239,68,68,0.16), var(--surface-1) 65%);
    border-color: rgba(239,68,68,0.28);
}}
.niq-hero-good {{
    background: linear-gradient(135deg, rgba(34,197,94,0.14), var(--surface-1) 65%);
    border-color: rgba(34,197,94,0.28);
}}
.niq-hero-neutral {{
    background: linear-gradient(135deg, rgba(91,141,239,0.12), var(--surface-1) 65%);
    border-color: var(--border-subtle);
}}
.niq-hero-eyebrow {{
    font-family: var(--font-data);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--ink-2);
}}
.niq-hero-title {{
    font-size: clamp(1.7rem, 2.6vw, 2.5rem);
    font-weight: 800;
    color: var(--ink-1);
    margin-top: 10px;
    letter-spacing: -0.02em;
}}
.niq-hero-sub {{
    color: var(--ink-2);
    margin-top: 10px;
    font-size: 1.02rem;
    max-width: 70ch;
    line-height: 1.55;
}}
.niq-hero-sub b {{ color: var(--ink-1); font-family: var(--font-data); font-variant-numeric: tabular-nums; }}

/* ---------- evidence meters ---------- */

.evidence-row {{ padding: 13px 0; border-bottom: 1px solid var(--border-subtle); }}
.evidence-row:last-child {{ border-bottom: none; }}
.evidence-head {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 7px; }}
.evidence-name {{ font-size: 0.86rem; color: var(--ink-1); font-weight: 600; }}
.evidence-pct {{ font-family: var(--font-data); font-size: 0.86rem; color: var(--ink-1); font-weight: 700; font-variant-numeric: tabular-nums; }}
.niq-track {{ height: 6px; border-radius: 999px; background: var(--surface-3); overflow: hidden; }}
.niq-track-fill {{ height: 100%; border-radius: 999px; }}

/* ---------- impact / contribution rows ---------- */

.impact-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border-subtle);
}}
.impact-row:last-child {{ border-bottom: none; }}
.impact-name {{ color: var(--ink-1); font-weight: 600; font-size: 0.92rem; }}
.impact-dim {{ color: var(--ink-3); font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }}

/* ---------- action / recommendation ---------- */

.niq-action {{
    background: linear-gradient(135deg, var(--accent-soft), var(--surface-1) 70%);
    border: 1px solid rgba(91,141,239,0.3);
    border-radius: var(--radius-lg);
    padding: 24px 26px;
}}

/* ---------- stepper (experiment lifecycle) ---------- */

.niq-stepper {{ display: flex; align-items: center; gap: 0; margin: 4px 0 18px; }}
.niq-step {{ display: flex; align-items: center; gap: 8px; }}
.niq-step-dot {{
    width: 22px; height: 22px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-data); font-size: 0.68rem; font-weight: 700;
    border: 2px solid var(--border-strong); color: var(--ink-3);
    background: var(--surface-2);
}}
.niq-step-label {{ font-size: 0.76rem; color: var(--ink-3); font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
.niq-step.is-active .niq-step-dot {{ border-color: var(--accent); color: var(--accent-strong); background: var(--accent-soft); }}
.niq-step.is-active .niq-step-label {{ color: var(--ink-1); }}
.niq-step.is-done .niq-step-dot {{ border-color: var(--good); color: var(--good); background: var(--good-soft); }}
.niq-step.is-done .niq-step-label {{ color: var(--ink-2); }}
.niq-step-connector {{ width: 34px; height: 2px; background: var(--border-strong); margin: 0 8px; }}
.niq-step-connector.is-done {{ background: var(--good); }}

/* ---------- empty / error states ---------- */

.niq-state {{
    text-align: center;
    padding: 46px 24px;
    border: 1px dashed var(--border-strong);
    border-radius: var(--radius-lg);
    background: var(--surface-1);
}}
.niq-state-icon {{ font-size: 1.8rem; margin-bottom: 10px; }}
.niq-state-title {{ font-size: 1.05rem; font-weight: 700; color: var(--ink-1); }}
.niq-state-body {{ color: var(--ink-2); font-size: 0.9rem; margin-top: 6px; max-width: 52ch; margin-left: auto; margin-right: auto; }}
.niq-state-error {{ border-color: rgba(239,68,68,0.35); background: linear-gradient(150deg, rgba(239,68,68,0.08), var(--surface-1)); }}

/* ---------- Streamlit widget overrides ---------- */

.stButton > button {{
    border-radius: 10px;
    border: 1px solid var(--border-strong);
    background: var(--surface-2);
    color: var(--ink-1);
    font-weight: 600;
    transition: all 120ms ease;
}}
.stButton > button:hover {{ border-color: var(--accent); color: var(--accent-strong); }}
.stButton > button[kind="primary"] {{
    background: var(--accent);
    border-color: var(--accent);
    color: #08101F;
}}
.stButton > button[kind="primary"]:hover {{ background: var(--accent-strong); color: #08101F; }}

.stTextInput input, .stNumberInput input,
.stSelectbox div[data-baseweb="select"], .stTextArea textarea {{
    background: var(--surface-2) !important;
    color: var(--ink-1) !important;
    border-color: var(--border-strong) !important;
    border-radius: 10px !important;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow: hidden;
}}

[data-testid="stMetricValue"] {{ font-family: var(--font-data); font-variant-numeric: tabular-nums; }}
[data-testid="stMetricLabel"] {{ color: var(--ink-3) !important; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.7rem !important; }}

[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface-1);
    border: 1px dashed var(--border-strong);
    border-radius: var(--radius-md);
}}

[data-testid="stChatMessage"] {{
    background: var(--surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
}}

.stProgress > div > div {{ background: var(--accent); }}

/* option_menu container tightening (nav is themed via its own config) */
.niq-brand {{
    font-family: var(--font-data);
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--ink-1);
    margin-bottom: 2px;
}}
.niq-brand-sub {{
    font-size: 0.68rem;
    color: var(--ink-3);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 20px;
}}

@media (prefers-reduced-motion: reduce) {{
    * {{ transition: none !important; animation: none !important; }}
}}

</style>
""",
        unsafe_allow_html=True,
    )
