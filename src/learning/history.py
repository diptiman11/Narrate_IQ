from pathlib import Path

import pandas as pd


EXPERIMENTS_PATH = Path(
    "data/processed/experiments.csv"
)

HISTORY_LOG_PATH = Path(
    "data/processed/experiment_history.csv"
)

SUMMARY_PATH = Path(
    "data/processed/hypothesis_history.csv"
)


def update_history() -> pd.DataFrame:
    if not EXPERIMENTS_PATH.exists():
        return pd.DataFrame()

    experiments = pd.read_csv(
        EXPERIMENTS_PATH
    )

    if experiments.empty:
        return pd.DataFrame()

    completed = experiments[
        experiments["status"] == "completed"
    ].copy()

    if completed.empty:
        return pd.DataFrame()

    history_columns = [
        "experiment_id",
        "date",
        "hypothesis",
        "confidence_score",
        "outcome",
        "measured_change_pct",
    ]

    available = [
        column
        for column in history_columns
        if column in completed.columns
    ]

    new_history = completed[
        available
    ].copy()

    if HISTORY_LOG_PATH.exists() and HISTORY_LOG_PATH.stat().st_size > 0:
        try:
            existing = pd.read_csv(
                HISTORY_LOG_PATH
            )
        except pd.errors.EmptyDataError:
            existing = pd.DataFrame()
    else:
        existing = pd.DataFrame()

    if existing.empty:
        history = new_history
    else:
        history = pd.concat(
            [
                existing,
                new_history,
            ],
            ignore_index=True,
        )

    history = history.drop_duplicates(
        subset=["experiment_id"],
        keep="last",
    )

    HISTORY_LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    history.to_csv(
        HISTORY_LOG_PATH,
        index=False,
    )

    # ---------------------------------------------
    # Aggregate historical reliability
    # ---------------------------------------------

    summary = (
        history.groupby("hypothesis")
        .agg(
            attempts=("experiment_id", "count"),
            successes=(
                "outcome",
                lambda x: (
                    x == "success"
                ).sum(),
            ),
            partials=(
                "outcome",
                lambda x: (
                    x == "partial"
                ).sum(),
            ),
            failures=(
                "outcome",
                lambda x: (
                    x == "failed"
                ).sum(),
            ),
        )
        .reset_index()
    )

    summary["success_rate"] = (
        summary["successes"]
        / summary["attempts"]
    )

    summary["non_failure_rate"] = (
        (
            summary["successes"]
            + summary["partials"]
        )
        / summary["attempts"]
    )

    summary["historical_reliability"] = (
        0.7 * summary["success_rate"]
        + 0.3 * summary["non_failure_rate"]
    )

    summary = summary.sort_values(
        "historical_reliability",
        ascending=False,
    ).reset_index(drop=True)

    summary.to_csv(
        SUMMARY_PATH,
        index=False,
    )

    return summary


def main() -> None:
    result = update_history()

    print(
        "\n=== Narrate IQ Experiment History ===\n"
    )

    if result.empty:
        print(
            "No completed experiments available."
        )
    else:
        print(
            result.to_string(
                index=False
            )
        )

    print(
        f"\nHistory log saved to: "
        f"{HISTORY_LOG_PATH}"
    )

    print(
        f"Summary saved to: "
        f"{SUMMARY_PATH}"
    )


if __name__ == "__main__":
    main()
