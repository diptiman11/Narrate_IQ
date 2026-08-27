from pathlib import Path

import pandas as pd


HYPOTHESIS_PATH = Path(
    "data/processed/hypotheses.csv"
)

EXPERIMENTS_PATH = Path(
    "data/processed/experiments.csv"
)


EXPERIMENT_DEFINITIONS = {
    "Sales volume deterioration": {
        "target_metric": "sales_units",
        "expected_direction": "increase",
        "success_threshold_pct": 5.0,
        "action": (
            "Investigate the sales-volume decline by region, "
            "product and channel. Prioritize high-volume "
            "products and regions with the largest unit losses."
        ),
    },
    "Inventory constraint": {
        "target_metric": "stockout_hours",
        "expected_direction": "decrease",
        "success_threshold_pct": 10.0,
        "action": (
            "Investigate inventory availability and "
            "replenishment. Prioritize products and "
            "warehouses with elevated stockout hours "
            "and declining stock."
        ),
    },
    "Marketing efficiency deterioration": {
        "target_metric": "marketing_conversion_rate",
        "expected_direction": "increase",
        "success_threshold_pct": 5.0,
        "action": (
            "Review campaign and channel performance "
            "to identify the source of declining marketing "
            "conversion efficiency before increasing "
            "marketing spend."
        ),
    },
}


def generate_experiments() -> pd.DataFrame:

    hypotheses = pd.read_csv(
        HYPOTHESIS_PATH
    )

    if hypotheses.empty:
        return pd.DataFrame()

    latest_date = hypotheses["date"].max()

    latest_hypotheses = hypotheses[
        hypotheses["date"] == latest_date
    ].copy()

    # -------------------------------------------------
    # Load existing experiment state if it exists.
    # -------------------------------------------------

    if EXPERIMENTS_PATH.exists():

        try:
            existing = pd.read_csv(
                EXPERIMENTS_PATH
            )
        except pd.errors.EmptyDataError:
            existing = pd.DataFrame()

    else:
        existing = pd.DataFrame()

    # -------------------------------------------------
    # Normalize existing columns.
    # -------------------------------------------------

    if not existing.empty:

        text_columns = [
            "experiment_id",
            "date",
            "hypothesis",
            "confidence",
            "status",
            "action",
            "target_metric",
            "expected_direction",
            "outcome",
        ]

        for column in text_columns:
            if column in existing.columns:
                existing[column] = existing[column].astype(
                    "string"
                )

    experiments = []

    for _, hypothesis in latest_hypotheses.iterrows():

        hypothesis_name = hypothesis["hypothesis"]

        definition = EXPERIMENT_DEFINITIONS.get(
            hypothesis_name
        )

        if definition is None:
            continue

        experiment_id = (
            f"{latest_date}-"
            f"{hypothesis_name.lower().replace(' ', '-')}"
        )

        # -------------------------------------------------
        # Preserve existing experiment state.
        # -------------------------------------------------

        if not existing.empty:

            matches = existing[
                existing["experiment_id"]
                == experiment_id
            ]

        else:

            matches = pd.DataFrame()

        if not matches.empty:

            previous = matches.iloc[-1].to_dict()

            # Completed/running experiments are preserved
            # exactly as they are.
            if previous.get("status") in {
                "running",
                "completed",
            }:

                experiments.append(
                    previous
                )

                continue

        # -------------------------------------------------
        # Create a new proposed experiment.
        # -------------------------------------------------

        experiments.append(
            {
                "experiment_id": experiment_id,
                "date": latest_date,
                "hypothesis": hypothesis_name,
                "hypothesis_rank": int(
                    hypothesis["hypothesis_rank"]
                ),
                "confidence_score": float(
                    hypothesis["confidence_score"]
                ),
                "confidence": hypothesis["confidence"],
                "status": "proposed",
                "action": definition["action"],
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

    result = pd.DataFrame(
        experiments
    )

    if not result.empty:

        result = result.sort_values(
            [
                "status",
                "hypothesis_rank",
            ],
            ascending=[
                True,
                True,
            ],
        ).reset_index(
            drop=True
        )

    EXPERIMENTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        EXPERIMENTS_PATH,
        index=False,
    )

    return result


def main() -> None:

    result = generate_experiments()

    print(
        "\n=== Narrate IQ State-Preserving "
        "Experiment Engine ===\n"
    )

    if result.empty:
        print(
            "No experiments generated."
        )
    else:
        print(
            result.to_string(
                index=False
            )
        )

    print(
        "\nSaved to: "
        "data/processed/experiments.csv"
    )


if __name__ == "__main__":
    main()
