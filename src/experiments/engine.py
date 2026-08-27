from pathlib import Path

import pandas as pd


HYPOTHESIS_PATH = "data/processed/hypotheses.csv"
RECOMMENDATION_PATH = "data/processed/recommendations.csv"

OUTPUT_PATH = "data/processed/experiments.csv"


EXPERIMENT_DEFINITIONS = {
    "Sales volume deterioration": {
        "action": (
            "Investigate the largest sales-unit losses by "
            "region, product and channel."
        ),
        "target_metric": "sales_units",
        "expected_direction": "increase",
        "success_threshold_pct": 5.0,
    },
    "Inventory constraint": {
        "action": (
            "Improve availability and replenishment for "
            "products and warehouses with elevated stockouts."
        ),
        "target_metric": "stockout_hours",
        "expected_direction": "decrease",
        "success_threshold_pct": 10.0,
    },
    "Marketing efficiency deterioration": {
        "action": (
            "Review underperforming campaigns and channels "
            "before increasing marketing spend."
        ),
        "target_metric": "marketing_conversion_rate",
        "expected_direction": "increase",
        "success_threshold_pct": 5.0,
    },
}


def generate_experiments() -> pd.DataFrame:
    hypotheses = pd.read_csv(HYPOTHESIS_PATH)
    recommendations = pd.read_csv(RECOMMENDATION_PATH)

    if hypotheses.empty:
        return pd.DataFrame()

    latest_date = hypotheses["date"].max()

    latest_hypotheses = hypotheses[
        hypotheses["date"] == latest_date
    ].copy()

    latest_recommendations = recommendations[
        recommendations["date"] == latest_date
    ].copy()

    experiments = []

    for _, hypothesis in latest_hypotheses.iterrows():

        hypothesis_name = hypothesis["hypothesis"]

        definition = EXPERIMENT_DEFINITIONS.get(
            hypothesis_name
        )

        if definition is None:
            continue

        recommendation_match = latest_recommendations[
            latest_recommendations["hypothesis"]
            == hypothesis_name
        ]

        recommendation = (
            recommendation_match.iloc[0]["recommendation"]
            if not recommendation_match.empty
            else definition["action"]
        )

        experiments.append(
            {
                "experiment_id": (
                    f"{latest_date}-"
                    f"{hypothesis_name.lower().replace(' ', '-')}"
                ),
                "date": latest_date,
                "hypothesis": hypothesis_name,
                "hypothesis_rank": hypothesis.get(
                    "hypothesis_rank",
                    None,
                ),
                "confidence_score": float(
                    hypothesis["confidence_score"]
                ),
                "confidence": hypothesis["confidence"],
                "status": "proposed",
                "action": recommendation,
                "target_metric": definition[
                    "target_metric"
                ],
                "expected_direction": definition[
                    "expected_direction"
                ],
                "success_threshold_pct": definition[
                    "success_threshold_pct"
                ],
                "baseline_value": None,
                "observed_value": None,
                "measured_change_pct": None,
                "outcome": None,
            }
        )

    return pd.DataFrame(experiments)


def main() -> None:
    result = generate_experiments()

    output = Path(OUTPUT_PATH)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        output,
        index=False,
    )

    print(
        "\n=== Narrate IQ Experiment Engine ===\n"
    )

    if result.empty:
        print("No experiments generated.")
    else:
        print(
            result.to_string(index=False)
        )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
