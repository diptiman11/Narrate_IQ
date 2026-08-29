"""
components.py
--------------
Reusable presentational building blocks used across every page.

None of these functions call the API or touch business logic - they
take already-fetched values and render them. Keeping them here means
each page file (views/*.py) stays focused on "what to show", not
"how to draw a box".
"""

from __future__ import annotations

import streamlit as st

from theme import T


# ============================================================
# small helpers
# ============================================================

def _kind_color(kind: str) -> str:
    return {
        "good": T["good"],
        "critical": T["critical"],
        "warning": T["warning"],
        "serious": T["serious"],
        "accent": T["accent"],
        "neutral": T["neutral"],
    }.get(kind, T["neutral"])


def signal_kind(value: float | None, invert: bool = False) -> str:
    """
    Map a signed number to a business-signal color kind.
    invert=True for metrics where "down" is good (e.g. cost, churn).
    """
    if value is None:
        return "neutral"
    value = float(value)
    if value == 0:
        return "neutral"
    positive = value > 0
    if invert:
        positive = not positive
    return "good" if positive else "critical"


# ============================================================
# flow section header (DATA -> INSIGHT -> EVIDENCE -> DECISION -> ACTION -> ...)
# ============================================================

def flow_step(index: str, flow_label: str, title: str) -> None:
    st.markdown(
        f"""
        <div class="niq-flow-step">
            <span class="flow-index">{index}</span>
            <span class="flow-label">{flow_label}</span>
            <span class="flow-title">{title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# hero / situation banner
# ============================================================

def hero_banner(eyebrow: str, title: str, subtitle_html: str, tone: str = "neutral") -> None:
    tone_class = {"good": "niq-hero-good", "critical": "niq-hero-critical"}.get(tone, "niq-hero-neutral")
    st.markdown(
        f"""
        <div class="niq-hero {tone_class}">
            <div class="niq-hero-eyebrow">{eyebrow}</div>
            <div class="niq-hero-title">{title}</div>
            <div class="niq-hero-sub">{subtitle_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# KPI tile
# ============================================================

def kpi_tile(label: str, value: str, delta_text: str | None = None, delta_kind: str = "neutral", sub: str | None = None) -> None:
    delta_html = ""
    if delta_text:
        arrow = "&#9650;" if delta_kind == "good" else ("&#9660;" if delta_kind == "critical" else "&#9679;")
        delta_html = f'<div class="delta delta-{delta_kind}">{arrow} {delta_text}</div>'
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="niq-card niq-card-tight">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# badges / status pills - always color + text, never color alone
# ============================================================

def badge(text: str, kind: str = "neutral", icon: str = "") -> str:
    prefix = f"{icon} " if icon else ""
    return f'<span class="niq-badge niq-badge-{kind}">{prefix}{text}</span>'


def outcome_badge(outcome: str | None) -> str:
    outcome = (outcome or "").lower()
    if outcome == "success":
        return badge("SUCCESS", "good", "&#10003;")
    if outcome == "partial":
        return badge("PARTIAL", "warning", "&#8226;")
    if outcome == "failed":
        return badge("FAILED", "critical", "&#10005;")
    return badge("PENDING", "neutral", "&#8231;")


def priority_badge(priority: str | None) -> str:
    """Priority is urgency, not a business-negative signal -> accent/warning, never red."""
    p = (priority or "").lower()
    if p == "high":
        return badge("HIGH PRIORITY", "warning", "&#9650;")
    if p == "medium":
        return badge("MEDIUM PRIORITY", "accent")
    if p == "low":
        return badge("LOW PRIORITY", "neutral")
    return badge(str(priority or "—").upper(), "neutral")


def status_badge(status: str | None) -> str:
    s = (status or "").lower()
    mapping = {
        "proposed": ("PROPOSED", "neutral", ""),
        "running": ("RUNNING", "accent", "&#9679;"),
        "completed": ("COMPLETED", "good", "&#10003;"),
    }
    label, kind, icon = mapping.get(s, (str(status or "—").upper(), "neutral", ""))
    return badge(label, kind, icon)


# ============================================================
# evidence meter (labelled progress bar)
# ============================================================

def evidence_meter(label: str, value: float | None) -> None:
    pct_val = 0.0 if value is None else max(0.0, min(1.0, float(value)))
    pct_display = "—" if value is None else f"{pct_val * 100:.0f}%"
    color = T["good"] if pct_val >= 0.66 else (T["warning"] if pct_val >= 0.4 else T["critical"])
    st.markdown(
        f"""
        <div class="evidence-row">
            <div class="evidence-head">
                <span class="evidence-name">{label}</span>
                <span class="evidence-pct">{pct_display}</span>
            </div>
            <div class="niq-track">
                <div class="niq-track-fill" style="width:{pct_val * 100:.0f}%; background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# impact row (segment / region / product / channel contribution)
# ============================================================

def impact_row(name: str, dimension: str, signed_value_text: str, kind: str) -> None:
    color = _kind_color(kind)
    st.markdown(
        f"""
        <div class="impact-row">
            <div>
                <div class="impact-name">{name}</div>
                <div class="impact-dim">{dimension}</div>
            </div>
            <div class="delta delta-{kind}" style="color:{color};">{signed_value_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# experiment lifecycle stepper
# ============================================================

def experiment_stepper(current_status: str) -> None:
    stages = ["proposed", "running", "completed"]
    labels = {"proposed": "Proposed", "running": "Running", "completed": "Completed"}
    current_idx = stages.index(current_status) if current_status in stages else 0

    parts = ['<div class="niq-stepper">']
    for i, stage in enumerate(stages):
        state = "is-done" if i < current_idx else ("is-active" if i == current_idx else "")
        marker = "&#10003;" if i < current_idx else str(i + 1)
        parts.append(
            f'<div class="niq-step {state}">'
            f'<div class="niq-step-dot">{marker}</div>'
            f'<div class="niq-step-label">{labels[stage]}</div>'
            f"</div>"
        )
        if i < len(stages) - 1:
            connector_state = "is-done" if i < current_idx else ""
            parts.append(f'<div class="niq-step-connector {connector_state}"></div>')
    parts.append("</div>")

    st.markdown("".join(parts), unsafe_allow_html=True)


# ============================================================
# empty / error states
# ============================================================

def empty_state(icon: str, title: str, body: str = "") -> None:
    st.markdown(
        f"""
        <div class="niq-state">
            <div class="niq-state-icon">{icon}</div>
            <div class="niq-state-title">{title}</div>
            <div class="niq-state-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def error_state(title: str, detail: str = "") -> None:
    st.markdown(
        f"""
        <div class="niq-state niq-state-error">
            <div class="niq-state-icon">&#9888;</div>
            <div class="niq-state-title">{title}</div>
            <div class="niq-state-body">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def action_card(priority_html: str, action_text: str) -> None:
    st.markdown(
        f"""
        <div class="niq-action">
            <div class="kpi-label">RECOMMENDED ACTION</div>
            <div style="margin:12px 0 14px;">{priority_html}</div>
            <div style="color:var(--ink-1); font-size:1.08rem; line-height:1.7;">{action_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
