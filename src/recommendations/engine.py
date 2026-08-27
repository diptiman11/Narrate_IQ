from pathlib import Path

import pandas as pd


HYPOTHESIS_PATH = "data/processed/hypotheses.csv"

OUTPUT_PATH = "data/processed/recommendations.csv"


def _priority_from_confidence(
    confidence_score: float,
) -> str:
    """
    Convert combined hypothesis confidence into
    an action priority.
    """

    if confidence_score >= 0.65:
        return "high"

    if confidence_score >= 0.35:
        return "medium"

    return "low"


def generate_recommendations() -> pd.DataFrame:
    hypotheses = pd.read_csv(HYPOTHESIS_PATH)

    recommendations = []

    for _, row in hypotheses.iterrows():

        hypothesis = row["hypothesis"]
        confidence = row["confidence"]
        confidence_score = float(
            row["confidence_score"]
        )

        recommendation = None

        priority = _priority_from_confidence(
            confidence_score
        )

        if hypothesis == "Sales volume deterioration":

            recommendation = (
                "Investigate the sales-volume decline by "
                "region, product and channel. Prioritize "
                "high-volume products and regions with the "
                "largest unit losses."
            )

        elif hypothesis == "Inventory constraint":

            recommendation = (
                "Investigate inventory availability and "
                "replenishment. Prioritize products and "
                "warehouses with elevated stockout hours "
                "and declining stock."
            )

        elif hypothesis == "Marketing efficiency deterioration":

            recommendation = (
                "Review campaign and channel performance "
                "to identify the source of declining "
                "marketing conversion efficiency before "
                "increasing marketing spend."
            )

        if recommendation:

            recommendations.append(
                {
                    "date": row["date"],
                    "hypothesis": hypothesis,
                    "status": row["status"],
                    "confidence": confidence,
                    "confidence_score": confidence_score,
                    "base_confidence_score": row.get(
                        "base_confidence_score",
                        None,
                    ),
                    "validation_score": row.get(
                        "validation_score",
                        None,
                    ),
                    "hypothesis_rank": row.get(
                        "hypothesis_rank",
                        None,
                    ),
                    "revenue_change_pct": row[
                        "revenue_change_pct"
                    ],
                    "evidence": row["evidence"],
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

        result["priority_rank"] = result[
            "priority"
        ].map(priority_order)

        result = result.sort_values(
            [
                "priority_rank",
                "confidence_score",
                "hypothesis_rank",
            ],
            ascending=[
                True,
                False,
                True,
            ],
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


def main() -> None:

    result = generate_recommendations()

    print(
        "\n=== Narrate IQ Hypothesis-Based "
        "Recommendation Engine ===\n"
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