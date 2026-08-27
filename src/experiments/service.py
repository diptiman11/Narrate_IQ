from pathlib import Path

import pandas as pd

from src.repositories.csv_repository import CSVRepository


EXPERIMENTS_FILENAME = "experiments.csv"


repository = CSVRepository()


def load_experiments() -> pd.DataFrame:
    if not repository.exists(EXPERIMENTS_FILENAME):
        raise FileNotFoundError(
            "experiments.csv not found. "
            "Run the experiment engine first."
        )

    experiments = repository.read(
        EXPERIMENTS_FILENAME
    )

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
        if column in experiments.columns:
            experiments[column] = experiments[column].astype(
                "string"
            )

    return experiments


def save_experiments(
    experiments: pd.DataFrame,
) -> None:
    repository.write(
        EXPERIMENTS_FILENAME,
        experiments,
    )


def start_experiment(
    experiment_id: str,
    baseline_value: float,
) -> dict:

    experiments = load_experiments()

    matches = experiments[
        experiments["experiment_id"] == experiment_id
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

    if status == "running":
        raise ValueError(
            "Experiment is already running."
        )

    experiments.at[index, "baseline_value"] = float(
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
        experiments["experiment_id"] == experiment_id
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
    observed_value = float(observed_value)

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