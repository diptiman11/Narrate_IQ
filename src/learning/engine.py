from pathlib import Path

import pandas as pd


EXPERIMENTS_PATH = Path(
    "data/processed/experiments.csv"
)

OUTPUT_PATH = Path(
    "data/processed/hypothesis_history.csv"
)


def generate_hypothesis_history() -> pd.DataFrame:
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

    history = (
        completed.groupby("hypothesis")
        .agg(
            attempts=("experiment_id", "count"),
            successes=("outcome", lambda x: (x == "success").sum()),
            partials=("outcome", lambda x: (x == "partial").sum()),
            failures=("outcome", lambda x: (x == "failed").sum()),
        )
        .reset_index()
    )

    history["success_rate"] = (
        history["successes"]
        / history["attempts"]
    )

    history["non_failure_rate"] = (
        (
            history["successes"]
            + history["partials"]
        )
        / history["attempts"]
    )

    history["historical_reliability"] = (
        0.7 * history["success_rate"]
        + 0.3 * history["non_failure_rate"]
    )

    history = history.sort_values(
        "historical_reliability",
        ascending=False,
    ).reset_index(drop=True)

    return history


def main() -> None:
    result = generate_hypothesis_history()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "\n=== Narrate IQ Hypothesis Learning Engine ===\n"
    )

    if result.empty:
        print(
            "No completed experiments available."
        )
    else:
        print(
            result.to_string(index=False)
        )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
