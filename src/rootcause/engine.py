from pathlib import Path

import pandas as pd


BASE_DIR = Path("data/processed")

HYPOTHESES_PATH = BASE_DIR / "hypotheses.csv"
DRILLDOWN_PATH = BASE_DIR / "sales_dimension_drilldown.csv"
RECOMMENDATIONS_PATH = BASE_DIR / "recommendations.csv"

OUTPUT_PATH = BASE_DIR / "root_cause_graph.csv"


def _build_hypothesis_rows(
    latest_hypotheses: pd.DataFrame,
    latest_recommendations: pd.DataFrame,
    latest_date: str,
) -> list[dict]:

    rows = []

    for _, hypothesis in latest_hypotheses.iterrows():

        hypothesis_name = hypothesis["hypothesis"]

        recommendation_match = latest_recommendations[
            latest_recommendations["hypothesis"]
            == hypothesis_name
        ]

        recommendation = (
            recommendation_match.iloc[0]["recommendation"]
            if not recommendation_match.empty
            else None
        )

        rows.append(
            {
                "date": latest_date,
                "node_type": "hypothesis",
                "parent": "revenue",
                "node": hypothesis_name,
                "rank": int(
                    hypothesis["hypothesis_rank"]
                ),
                "confidence_score": float(
                    hypothesis["confidence_score"]
                ),
                "confidence": hypothesis[
                    "confidence"
                ],
                "validation_score": float(
                    hypothesis["validation_score"]
                ),
                "status": hypothesis["status"],
                "recommendation": recommendation,
                "dimension": None,
                "dimension_value": None,
                "unit_change": None,
                "unit_change_pct": None,
                "revenue_change": None,
                "revenue_change_pct": None,
                "contribution_share_pct": None,
            }
        )

    return rows


def _build_segment_rows(
    drilldown: pd.DataFrame,
    latest_date: str,
) -> list[dict]:

    rows = []

    if drilldown.empty:
        return rows

    # Only sales-volume deterioration currently has
    # dimension-level evidence.
    subset = drilldown[
        drilldown["unit_change"] < 0
    ].copy()

    if subset.empty:
        return rows

    dimensions = [
        "region",
        "product_id",
        "channel",
    ]

    for dimension in dimensions:

        dimension_rows = subset[
            subset["dimension"] == dimension
        ].copy()

        if dimension_rows.empty:
            continue

        dimension_rows = dimension_rows.sort_values(
            "unit_change",
            ascending=True,
        )

        total_loss = abs(
            float(
                dimension_rows["unit_change"].sum()
            )
        )

        if total_loss == 0:
            continue

        # Keep the five most negative segments per dimension.
        for _, row in dimension_rows.head(5).iterrows():

            unit_change = float(
                row["unit_change"]
            )

            contribution_share = (
                abs(unit_change)
                / total_loss
                * 100
            )

            unit_change_pct = (
                float(row["unit_change_pct"])
                if pd.notna(
                    row["unit_change_pct"]
                )
                else None
            )

            revenue_change = float(
                row["revenue_change"]
            )

            revenue_change_pct = (
                float(
                    row["revenue_change_pct"]
                )
                if pd.notna(
                    row["revenue_change_pct"]
                )
                else None
            )

            rows.append(
                {
                    "date": latest_date,
                    "node_type": "segment",
                    "parent": (
                        "Sales volume deterioration"
                    ),
                    "node": (
                        f"{dimension}:"
                        f"{row[dimension]}"
                    ),
                    "rank": None,
                    "confidence_score": None,
                    "confidence": None,
                    "validation_score": None,
                    "status": None,
                    "recommendation": None,
                    "dimension": dimension,
                    "dimension_value": row[
                        dimension
                    ],
                    "unit_change": unit_change,
                    "unit_change_pct": (
                        unit_change_pct
                    ),
                    "revenue_change": revenue_change,
                    "revenue_change_pct": (
                        revenue_change_pct
                    ),
                    "contribution_share_pct": round(
                        contribution_share,
                        2,
                    ),
                }
            )

    return rows


def build_root_cause_graph() -> pd.DataFrame:

    hypotheses = pd.read_csv(
        HYPOTHESES_PATH
    )

    drilldown = pd.read_csv(
        DRILLDOWN_PATH
    )

    recommendations = pd.read_csv(
        RECOMMENDATIONS_PATH
    )

    if hypotheses.empty:
        return pd.DataFrame()

    latest_date = hypotheses["date"].max()

    latest_hypotheses = hypotheses[
        hypotheses["date"] == latest_date
    ].copy()

    latest_drilldown = drilldown[
        drilldown["date"] == latest_date
    ].copy()

    latest_recommendations = recommendations[
        recommendations["date"] == latest_date
    ].copy()

    rows = []

    rows.extend(
        _build_hypothesis_rows(
            latest_hypotheses,
            latest_recommendations,
            latest_date,
        )
    )

    rows.extend(
        _build_segment_rows(
            latest_drilldown,
            latest_date,
        )
    )

    result = pd.DataFrame(rows)

    if not result.empty:

        result = result.sort_values(
            [
                "node_type",
                "rank",
                "dimension",
                "unit_change",
            ],
            ascending=[
                True,
                True,
                True,
                True,
            ],
            na_position="last",
        ).reset_index(drop=True)

    return result


def main() -> None:

    result = build_root_cause_graph()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "\n=== Narrate IQ Root Cause Graph ===\n"
    )

    if result.empty:
        print("No root-cause graph generated.")
    else:
        print(
            result.to_string(index=False)
        )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
