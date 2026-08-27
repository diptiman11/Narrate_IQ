from pathlib import Path

import pandas as pd


EXPERIMENTS_PATH = Path(
    "data/processed/experiments.csv"
)


def load_experiments() -> pd.DataFrame:
    if not EXPERIMENTS_PATH.exists():
        raise FileNotFoundError(
            "experiments.csv not found. "
            "Run the experiment engine first."
        )

    return pd.read_csv(EXPERIMENTS_PATH)


def save_experiments(
    experiments: pd.DataFrame,
) -> None:
    EXPERIMENTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    experiments.to_csv(
        EXPERIMENTS_PATH,
        index=False,
    )


def start_experiment(
    experiment_id: str,
    baseline_value: float,
) -> dict:
    experiments = load_experiments()

    matches = experiments[
        experiments["experiment_id"]
        == experiment_id
    ]

    if matches.empty:
        raise ValueError(
            f"Experiment '{experiment_id}' not found."
        )

    index = matches.index[0]

    status = experiments.at[index, "status"]

    if status == "completed":
        raise ValueError(
            "Completed experiments cannot be restarted."
        )

    experiments.at[index, "baseline_value"] = (
        baseline_value
    )

    experiments.at[index, "status"] = "running"

    save_experiments(experiments)

    return experiments.loc[index].to_dict()


def complete_experiment(
    experiment_id: str,
    observed_value: float,
) -> dict:
    experiments = load_experiments()

    matches = experiments[
        experiments["experiment_id"]
        == experiment_id
    ]

    if matches.empty:
        raise ValueError(
            f"Experiment '{experiment_id}' not found."
        )

    index = matches.index[0]

    status = experiments.at[index, "status"]
    baseline = experiments.at[index, "baseline_value"]

    if status != "running":
        raise ValueError(
            "Experiment must be running before "
            "an outcome can be recorded."
        )

    if pd.isna(baseline):
        raise ValueError(
            "Experiment has no baseline value."
        )

    baseline = float(baseline)

    if baseline == 0:
        raise ValueError(
            "Baseline value cannot be zero."
        )

    measured_change = (
        (observed_value - baseline)
        / abs(baseline)
        * 100
    )

    expected_direction = experiments.at[
        index,
        "expected_direction",
    ]

    threshold = float(
        experiments.at[
            index,
            "success_threshold_pct",
        ]
    )

    if expected_direction == "increase":

        if measured_change >= threshold:
            outcome = "success"

        elif measured_change > 0:
            outcome = "partial"

        else:
            outcome = "failed"

    elif expected_direction == "decrease":

        if measured_change <= -threshold:
            outcome = "success"

        elif measured_change < 0:
            outcome = "partial"

        else:
            outcome = "failed"

    else:
        outcome = "unknown"

    experiments.at[index, "observed_value"] = (
        observed_value
    )

    experiments.at[index, "measured_change_pct"] = (
        measured_change
    )

    experiments.at[index, "outcome"] = outcome

    experiments.at[index, "status"] = "completed"

    save_experiments(experiments)

    return experiments.loc[index].to_dict()
