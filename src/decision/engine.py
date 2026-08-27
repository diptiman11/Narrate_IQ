from pathlib import Path

import json
import pandas as pd


BASE_DIR = Path("data/processed")

KPI_PATH = BASE_DIR / "daily_kpis.csv"
HYPOTHESIS_PATH = BASE_DIR / "hypotheses.csv"
VALIDATION_PATH = BASE_DIR / "evidence_validation.csv"
ROOT_CAUSE_PATH = BASE_DIR / "root_cause_graph.csv"
RECOMMENDATION_PATH = BASE_DIR / "recommendations.csv"
EXPERIMENT_PATH = BASE_DIR / "experiments.csv"
HISTORY_PATH = BASE_DIR / "hypothesis_history.csv"
EVENT_PATH = BASE_DIR / "event_context.csv"

OUTPUT_PATH = BASE_DIR / "decision_object.json"


def _read_optional(path: Path) -> pd.DataFrame:
    """
    Read an optional CSV safely.

    Missing or empty files return an empty DataFrame
    instead of crashing the decision engine.
    """
    if not path.exists():
        return pd.DataFrame()

    if path.stat().st_size == 0:
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass

    return value


def build_decision_object() -> dict:
    kpis = pd.read_csv(KPI_PATH)
    hypotheses = pd.read_csv(HYPOTHESIS_PATH)
    validation = pd.read_csv(VALIDATION_PATH)
    root_cause = pd.read_csv(ROOT_CAUSE_PATH)
    recommendations = pd.read_csv(RECOMMENDATION_PATH)
    experiments = pd.read_csv(EXPERIMENT_PATH)

    history = _read_optional(HISTORY_PATH)
    events = _read_optional(EVENT_PATH)

    if kpis.empty or hypotheses.empty:
        return {}

    latest_date = kpis["date"].max()

    latest_kpi = kpis[
        kpis["date"] == latest_date
    ].iloc[-1]

    latest_hypotheses = hypotheses[
        hypotheses["date"] == latest_date
    ].sort_values(
        "hypothesis_rank"
    )

    if latest_hypotheses.empty:
        return {}

    leading = latest_hypotheses.iloc[0]

    hypothesis_name = leading["hypothesis"]

    # ---------------------------------------------
    # Validation
    # ---------------------------------------------

    validation_match = validation[
        (validation["date"] == latest_date)
        & (
            validation["hypothesis"]
            == hypothesis_name
        )
    ]

    validation_row = (
        validation_match.iloc[0]
        if not validation_match.empty
        else None
    )

    # ---------------------------------------------
    # Recommendation
    # ---------------------------------------------

    recommendation_match = recommendations[
        (recommendations["date"] == latest_date)
        & (
            recommendations["hypothesis"]
            == hypothesis_name
        )
    ]

    recommendation_row = (
        recommendation_match.iloc[0]
        if not recommendation_match.empty
        else None
    )

    # ---------------------------------------------
    # Experiment
    # ---------------------------------------------

    experiment_match = experiments[
        experiments["hypothesis"]
        == hypothesis_name
    ]

    experiment_row = (
        experiment_match.sort_values(
            "date"
        ).iloc[-1]
        if not experiment_match.empty
        else None
    )

    # ---------------------------------------------
    # Historical learning
    # ---------------------------------------------

    history_match = (
        history[
            history["hypothesis"]
            == hypothesis_name
        ]
        if not history.empty
        else pd.DataFrame()
    )

    history_row = (
        history_match.iloc[0]
        if not history_match.empty
        else None
    )

    # ---------------------------------------------
    # Top affected segments
    # ---------------------------------------------

    segments = root_cause[
        (root_cause["date"] == latest_date)
        & (
            root_cause["node_type"]
            == "segment"
        )
        & (
            root_cause["parent"]
            == hypothesis_name
        )
    ].copy()

    segments = segments.sort_values(
        "unit_change",
        ascending=True,
    ).head(10)

    top_segments = []

    for _, row in segments.iterrows():
        top_segments.append(
            {
                "dimension": _clean_value(
                    row["dimension"]
                ),
                "value": _clean_value(
                    row["dimension_value"]
                ),
                "unit_change": _clean_value(
                    row["unit_change"]
                ),
                "unit_change_pct": _clean_value(
                    row["unit_change_pct"]
                ),
                "revenue_change": _clean_value(
                    row["revenue_change"]
                ),
                "revenue_change_pct": _clean_value(
                    row["revenue_change_pct"]
                ),
                "contribution_share_pct": _clean_value(
                    row[
                        "contribution_share_pct"
                    ]
                ),
            }
        )

    # ---------------------------------------------
    # Business events
    # ---------------------------------------------

    relevant_events = []

    if not events.empty:

        recent_events = events[
            events["event_date"] <= latest_date
        ].sort_values(
            "event_date",
            ascending=False,
        ).head(5)

        for _, event in recent_events.iterrows():

            relevant_events.append(
                {
                    "event_date": _clean_value(
                        event["event_date"]
                    ),
                    "event_name": _clean_value(
                        event["event_name"]
                    ),
                    "event_type": _clean_value(
                        event["event_type"]
                    ),
                    "event_category": _clean_value(
                        event["event_category"]
                    ),
                    "description": _clean_value(
                        event["description"]
                    ),
                }
            )

    # ---------------------------------------------
    # Build decision object
    # ---------------------------------------------

    decision = {
        "date": latest_date,

        "problem": (
            "Revenue deterioration"
            if float(
                latest_kpi["revenue_wow_pct"]
            ) < 0
            else "Revenue movement"
        ),

        "kpi": {
            "revenue": float(
                latest_kpi["revenue"]
            ),
            "revenue_change_pct": (
                float(
                    latest_kpi[
                        "revenue_wow_pct"
                    ]
                )
                * 100
            ),
            "units_sold": float(
                latest_kpi["units_sold"]
            ),
        },

        "leading_hypothesis": {
            "name": hypothesis_name,
            "rank": int(
                leading["hypothesis_rank"]
            ),
            "confidence_score": float(
                leading["confidence_score"]
            ),
            "confidence": leading["confidence"],
            "status": leading["status"],
        },

        "validation": {
            "validation_score": (
                _clean_value(
                    validation_row[
                        "validation_score"
                    ]
                )
                if validation_row is not None
                else None
            ),
            "statistical_score": (
                _clean_value(
                    validation_row[
                        "statistical_score"
                    ]
                )
                if validation_row is not None
                else None
            ),
            "event_context_score": (
                _clean_value(
                    validation_row[
                        "event_context_score"
                    ]
                )
                if validation_row is not None
                else None
            ),
            "segment_evidence_score": (
                _clean_value(
                    validation_row[
                        "segment_evidence_score"
                    ]
                )
                if validation_row is not None
                else None
            ),
            "supporting_evidence": (
                _clean_value(
                    validation_row[
                        "supporting_evidence"
                    ]
                )
                if validation_row is not None
                else leading["evidence"]
            ),
        },

        "top_segments": top_segments,

        "business_events": relevant_events,

        "recommendation": (
            {
                "priority": _clean_value(
                    recommendation_row[
                        "priority"
                    ]
                ),
                "action": _clean_value(
                    recommendation_row[
                        "recommendation"
                    ]
                ),
            }
            if recommendation_row is not None
            else None
        ),

        "experiment": (
            {
                "experiment_id": _clean_value(
                    experiment_row[
                        "experiment_id"
                    ]
                ),
                "status": _clean_value(
                    experiment_row["status"]
                ),
                "target_metric": _clean_value(
                    experiment_row[
                        "target_metric"
                    ]
                ),
                "expected_direction": _clean_value(
                    experiment_row[
                        "expected_direction"
                    ]
                ),
                "success_threshold_pct": (
                    _clean_value(
                        experiment_row[
                            "success_threshold_pct"
                        ]
                    )
                ),
                "baseline_value": _clean_value(
                    experiment_row[
                        "baseline_value"
                    ]
                ),
                "observed_value": _clean_value(
                    experiment_row[
                        "observed_value"
                    ]
                ),
                "measured_change_pct": (
                    _clean_value(
                        experiment_row[
                            "measured_change_pct"
                        ]
                    )
                ),
                "outcome": _clean_value(
                    experiment_row["outcome"]
                ),
            }
            if experiment_row is not None
            else None
        ),

        "historical_learning": (
            {
                "attempts": int(
                    history_row["attempts"]
                ),
                "successes": int(
                    history_row["successes"]
                ),
                "partials": int(
                    history_row["partials"]
                ),
                "failures": int(
                    history_row["failures"]
                ),
                "historical_reliability": float(
                    history_row[
                        "historical_reliability"
                    ]
                ),
            }
            if history_row is not None
            else None
        ),
    }

    return decision


def main() -> None:

    result = build_decision_object()

    if not result:
        print(
            "\n=== Narrate IQ Decision Engine ===\n"
        )
        print(
            "No decision object could be generated."
        )
        return

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            result,
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
    )

    print(
        "\n=== Narrate IQ Decision Engine ===\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            allow_nan=False,
        )
    )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
