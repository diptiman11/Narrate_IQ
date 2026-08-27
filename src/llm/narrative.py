from pathlib import Path

import pandas as pd


KPI_PATH = "data/processed/daily_kpis.csv"
HYPOTHESIS_PATH = "data/processed/hypotheses.csv"
RECOMMENDATION_PATH = "data/processed/recommendations.csv"

OUTPUT_PATH = "data/processed/business_narrative.txt"


def generate_narrative() -> str:
    kpis = pd.read_csv(KPI_PATH)
    hypotheses = pd.read_csv(HYPOTHESIS_PATH)
    recommendations = pd.read_csv(RECOMMENDATION_PATH)

    if kpis.empty:
        return "No KPI data available."

    latest = kpis.iloc[-1]

    date = latest["date"]
    revenue = float(latest["revenue"])
    revenue_wow = float(latest["revenue_wow_pct"]) * 100
    units = float(latest["units_sold"])

    latest_hypotheses = hypotheses[
        hypotheses["date"] == date
    ].copy()

    latest_recommendations = recommendations[
        recommendations["date"] == date
    ].copy()

    narrative = []

    narrative.append(
        f"Business Performance Summary — {date}"
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

    # -------------------------------------------------
    # Ranked hypotheses
    # -------------------------------------------------

    if not latest_hypotheses.empty:

        latest_hypotheses = latest_hypotheses.sort_values(
            "confidence_score",
            ascending=False,
        )

        winner = latest_hypotheses.iloc[0]

        narrative.append("")

        narrative.append(
            "Leading explanation:"
        )

        narrative.append(
            f"{winner['hypothesis']} "
            f"({winner['confidence']} confidence, "
            f"score {float(winner['confidence_score']):.2f})."
        )

        narrative.append(
            f"Evidence: {winner['evidence']}."
        )

        if (
            "validation_score" in winner
            and pd.notna(winner["validation_score"])
        ):
            narrative.append(
                f"Evidence validation score: "
                f"{float(winner['validation_score']):.2f}."
            )

        # Competing explanations

        if len(latest_hypotheses) > 1:

            narrative.append("")

            narrative.append(
                "Competing explanations:"
            )

            for _, row in latest_hypotheses.iloc[1:].iterrows():

                score = float(
                    row["confidence_score"]
                )

                narrative.append(
                    f"- {row['hypothesis']}: "
                    f"{row['confidence']} confidence "
                    f"(score {score:.2f})."
                )

    # -------------------------------------------------
    # Recommendations
    # -------------------------------------------------

    if not latest_recommendations.empty:

        narrative.append("")

        narrative.append(
            "Recommended actions:"
        )

        for _, row in latest_recommendations.head(3).iterrows():

            narrative.append(
                f"- [{str(row['priority']).upper()}] "
                f"{row['recommendation']}"
            )

    return "\n".join(narrative)


def main() -> None:

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