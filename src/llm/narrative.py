from pathlib import Path

import pandas as pd


KPI_PATH = "data/processed/daily_kpis.csv"
ATTRIBUTION_PATH = "data/processed/driver_attribution.csv"
CONFIDENCE_PATH = "data/processed/confidence_scores.csv"
RECOMMENDATION_PATH = "data/processed/recommendations.csv"

OUTPUT_PATH = "data/processed/business_narrative.txt"


def generate_narrative() -> str:

    kpis = pd.read_csv(KPI_PATH)
    attribution = pd.read_csv(ATTRIBUTION_PATH)
    confidence = pd.read_csv(CONFIDENCE_PATH)
    recommendations = pd.read_csv(RECOMMENDATION_PATH)

    latest = kpis.iloc[-1]

    date = latest["date"]
    revenue = latest["revenue"]
    revenue_wow = latest["revenue_wow_pct"] * 100
    units = latest["units_sold"]

    latest_attribution = attribution[
        attribution["date"] == date
    ].copy()

    latest_confidence = confidence[
        confidence["date"] == date
    ].copy()

    narrative = []

    narrative.append(
        f"Business Performance Summary - {date}"
    )

    narrative.append("")

    direction = (
        "increased"
        if revenue_wow > 0
        else "declined"
    )

    narrative.append(
        f"Revenue {direction} by "
        f"{abs(revenue_wow):.2f}% week-over-week "
        f"to ${revenue:,.0f}."
    )

    narrative.append(
        f"Units sold were {units:,.0f}."
    )

    # Primary driver
    if not latest_attribution.empty:

        primary = latest_attribution.iloc[0]

        driver = primary["driver"]
        driver_change = primary["driver_change_pct"]
        importance = primary["model_importance_pct"]

        confidence_match = latest_confidence[
            latest_confidence["driver"] == driver
        ]

        confidence_level = "unknown"

        if not confidence_match.empty:
            confidence_level = confidence_match.iloc[0][
                "confidence"
            ]

        narrative.append("")

        narrative.append(
            f"The primary associated driver was "
            f"{driver}, which changed by "
            f"{driver_change:+.2f}%. "
            f"The model assigned this feature "
            f"{importance:.2f}% of relative feature importance, "
            f"with {confidence_level} confidence."
        )

        narrative.append(
            "This should be interpreted as an associated driver "
            "rather than proof of causation."
        )

    # Other drivers
    if len(latest_attribution) > 1:

        narrative.append("")
        narrative.append("Other observed driver movements:")

        for _, row in latest_attribution.iloc[1:4].iterrows():

            narrative.append(
                f"- {row['driver']}: "
                f"{row['driver_change_pct']:+.2f}%"
            )

    # Recommendations
    if not recommendations.empty:

        narrative.append("")
        narrative.append("Recommended actions:")

        for _, row in recommendations.head(3).iterrows():

            narrative.append(
                f"- [{row['priority'].upper()}] "
                f"{row['recommendation']}"
            )

    return "\n".join(narrative)


def main():

    narrative = generate_narrative()

    output = Path(OUTPUT_PATH)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        narrative,
        encoding="utf-8",
    )

    print(
        "\n=== Narrate IQ Business Narrative ===\n"
    )

    print(narrative)

    print(
        "\nSaved to: "
        "data/processed/business_narrative.txt"
    )


if __name__ == "__main__":
    main()
