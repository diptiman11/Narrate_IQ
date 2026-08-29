"""
data_quality.py
----------------
A quick, local, frontend-only quality check for an uploaded CSV.

This is deliberately shallow (row count, missing values, duplicate
rows) - it is a UX signal shown before the file reaches the real
ingestion + validation pipeline (src.* modules on the backend), not a
replacement for it. Nothing here changes what the backend accepts.
"""

from __future__ import annotations

import pandas as pd


def quick_quality_score(df: pd.DataFrame) -> dict:
    """Return a 0-100 score plus the component reasons behind it."""

    if df.empty:
        return {"score": 0, "rows": 0, "columns": 0, "missing_pct": 100.0, "duplicate_pct": 0.0}

    rows, cols = df.shape
    missing_pct = float(df.isna().mean().mean() * 100) if cols else 100.0
    duplicate_pct = float(df.duplicated().mean() * 100) if rows else 0.0

    score = 100.0
    score -= min(missing_pct * 1.2, 60)
    score -= min(duplicate_pct * 0.8, 25)
    if rows < 10:
        score -= 20
    score = max(0.0, min(100.0, score))

    return {
        "score": round(score),
        "rows": rows,
        "columns": cols,
        "missing_pct": round(missing_pct, 1),
        "duplicate_pct": round(duplicate_pct, 1),
    }


def score_band(score: int) -> str:
    """Map a 0-100 score to a semantic kind used by components.badge()."""
    if score >= 80:
        return "good"
    if score >= 55:
        return "warning"
    return "critical"
