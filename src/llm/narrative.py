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

    latest = kpis.iloc[-1]

    date = latest["date"]
    revenue = float(latest["revenue"])
    revenue_wow = float(latest["revenue_wow_pct"]) * 100
    units = float(latest["units_sold"])

    narrative = []

    narrative.append(
        f"Business Performance Summary — {date}"
    )

    narrative.append("")

    direction = "increased" if revenue_wow > 0 else "declined"

    narrative.append(
        f"Revenue {direction} by {abs(revenue_wow):.2f}% "
        f"week-over-week to ${revenue:,.0f}."
    )

    narrative.append(
        f"Units sold were {units:,.0f}."
    )

    # Hypotheses
    if not hypotheses.empty:

        narrative.append("")
        narrative.append("Key business hypotheses:")

        for _, row in hypotheses.head(3).iterrows():

            narrative.append(
                f"- {row['hypothesis']} "
                f"({row['confidence']} confidence): "
                f"{row['evidence']}."
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