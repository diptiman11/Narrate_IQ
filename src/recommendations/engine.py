from pathlib import Path

import pandas as pd


CONFIDENCE_PATH = "data/processed/confidence_scores.csv"
KPI_PATH = "data/processed/daily_kpis.csv"

OUTPUT_PATH = "data/processed/recommendations.csv"


def generate_recommendations() -> pd.DataFrame:

    confidence = pd.read_csv(CONFIDENCE_PATH)
    kpis = pd.read_csv(KPI_PATH)

    latest_date = kpis["date"].max()

    latest_kpi = kpis[
        kpis["date"] == latest_date
    ].iloc[0]

    recommendations = []

    for _, row in confidence.iterrows():

        driver = row["driver"]
        change = float(row["driver_change_pct"])
        confidence_level = row["confidence"]

        recommendation = None
        priority = "low"

        if driver == "sales_units" and change < -5:

            recommendation = (
                "Investigate the sales-volume decline by "
                "region, product and channel. Prioritize "
                "high-volume products and regions with the "
                "largest unit losses."
            )
            priority = "high"

        elif driver == "stockout_hours" and change > 10:

            recommendation = (
                "Investigate inventory availability and "
                "replenishment. Prioritize products and "
                "warehouses with elevated stockout hours."
            )
            priority = "high"

        elif driver == "closing_stock" and change < -5:

            recommendation = (
                "Review inventory levels and replenishment "
                "planning to determine whether declining "
                "stock is constraining sales."
            )
            priority = "medium"

        elif driver == "marketing_spend" and change > 10:

            recommendation = (
                "Review marketing spend efficiency and "
                "compare campaign-level conversion performance "
                "before increasing spend further."
            )
            priority = "medium"

        elif driver == "marketing_conversion_rate" and change < -5:

            recommendation = (
                "Review campaign and channel performance "
                "to identify the source of declining "
                "marketing conversion efficiency."
            )
            priority = "medium"

        elif driver == "marketing_clicks" and change < -10:

            recommendation = (
                "Review campaign reach and channel traffic "
                "to identify the cause of declining clicks."
            )
            priority = "medium"

        elif driver == "marketing_conversions" and change < -10:

            recommendation = (
                "Review campaign targeting and landing-page "
                "performance because marketing conversions "
                "are declining."
            )
            priority = "medium"

        if recommendation:

            recommendations.append(
                {
                    "date": latest_date,
                    "driver": driver,
                    "driver_change_pct": change,
                    "confidence": confidence_level,
                    "confidence_score": row[
                        "confidence_score"
                    ],
                    "priority": priority,
                    "recommendation": recommendation,
                }
            )

    result = pd.DataFrame(recommendations)

    if not result.empty:

        priority_order = {
            "high": 1,
            "medium": 2,
            "low": 3,
        }

        result["priority_rank"] = (
            result["priority"]
            .map(priority_order)
        )

        result = result.sort_values(
            ["priority_rank", "confidence_score"],
            ascending=[True, False],
        )

        result = result.drop(
            columns=["priority_rank"]
        )

    output = Path(OUTPUT_PATH)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        output,
        index=False,
    )

    return result


def main():

    result = generate_recommendations()

    print(
        "\n=== Narrate IQ Recommendation Engine ===\n"
    )

    if result.empty:

        print(
            "No actionable recommendations "
            "were generated."
        )

    else:

        print(
            result.to_string(index=False)
        )

    print(
        "\nSaved to: "
        "data/processed/recommendations.csv"
    )


if __name__ == "__main__":
    main()