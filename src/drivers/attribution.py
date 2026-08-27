from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance


INPUT_PATH = "data/processed/driver_evidence.csv"
OUTPUT_PATH = "data/processed/driver_attribution.csv"


FEATURES = [
    "sales_units",
    "marketing_spend",
    "marketing_clicks",
    "marketing_conversions",
    "marketing_conversion_rate",
    "stockout_hours",
    "closing_stock",
]


def build_change_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").copy()

    # Day-over-day changes.
    for column in FEATURES:
        df[f"{column}_change"] = df[column].pct_change()

    df["revenue_change"] = df["sales_revenue"].pct_change()

    return df


def run_attribution() -> pd.DataFrame:

    df = pd.read_csv(INPUT_PATH)
    df["date"] = pd.to_datetime(df["date"])

    df = build_change_features(df)

    change_features = [
        f"{column}_change"
        for column in FEATURES
    ]

    model_df = df[
        ["date", "sales_revenue", "revenue_change", *change_features]
    ].replace(
        [float("inf"), float("-inf")],
        pd.NA,
    ).dropna()

    if len(model_df) < 50:
        raise ValueError(
            f"Not enough usable rows: {len(model_df)}"
        )

    X = model_df[change_features]
    y = model_df["revenue_change"]

    split = int(len(model_df) * 0.8)

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=5,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    permutation = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=20,
        random_state=42,
        scoring="r2",
    )

    importance = pd.DataFrame(
        {
            "feature": change_features,
            "importance": permutation.importances_mean,
        }
    )

    importance["driver"] = (
        importance["feature"]
        .str.replace("_change", "", regex=False)
    )

    importance["importance"] = importance["importance"].clip(lower=0)

    total = importance["importance"].sum()

    if total > 0:
        importance["importance_pct"] = (
            importance["importance"] / total * 100
        )
    else:
        importance["importance_pct"] = 0

    latest = model_df.iloc[-1]

    rows = []

    for _, item in importance.iterrows():

        driver = item["driver"]
        change = latest[f"{driver}_change"]

        rows.append(
            {
                "date": latest["date"],
                "driver": driver,
                "driver_change_pct": change * 100,
                "model_importance_pct": item["importance_pct"],
            }
        )

    result = pd.DataFrame(rows)

    result["direction"] = result["driver_change_pct"].apply(
        lambda x: (
            "increase"
            if x > 0
            else "decrease"
            if x < 0
            else "flat"
        )
    )

    result["impact_rank"] = (
        result["model_importance_pct"]
        .rank(
            ascending=False,
            method="first",
        )
        .astype(int)
    )

    result = result.sort_values("impact_rank")

    output = Path(OUTPUT_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)

    return result


def main():

    result = run_attribution()

    print("\n=== Narrate IQ Driver Attribution ===\n")

    print(
        result[
            [
                "date",
                "driver",
                "driver_change_pct",
                "model_importance_pct",
                "direction",
                "impact_rank",
            ]
        ].to_string(index=False)
    )

    print(
        "\nSaved to: "
        "data/processed/driver_attribution.csv"
    )


if __name__ == "__main__":
    main()