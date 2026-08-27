from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


INPUT_PATH = "data/processed/driver_evidence.csv"
OUTPUT_PATH = "data/processed/ml_driver_importance.csv"


BASE_FEATURES = [
    "sales_units",
    "marketing_spend",
    "marketing_clicks",
    "marketing_conversions",
    "marketing_conversion_rate",
    "stockout_hours",
    "closing_stock",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").copy()

    # Previous-day information
    for feature in BASE_FEATURES:
        df[f"{feature}_lag1"] = df[feature].shift(1)

    # Seven-day historical information
    for feature in BASE_FEATURES:
        df[f"{feature}_lag7"] = df[feature].shift(7)

    # Recent trends
    df["revenue_lag1"] = df["sales_revenue"].shift(1)
    df["revenue_lag7"] = df["sales_revenue"].shift(7)

    df["revenue_rolling7"] = (
        df["sales_revenue"]
        .shift(1)
        .rolling(7)
        .mean()
    )

    return df


def train_model():

    df = pd.read_csv(INPUT_PATH)
    df["date"] = pd.to_datetime(df["date"])

    df = build_features(df)

    feature_columns = [
        column
        for column in df.columns
        if column.endswith("_lag1")
        or column.endswith("_lag7")
        or column == "revenue_rolling7"
    ]

    model_df = df[
        ["date", "sales_revenue", *feature_columns]
    ].copy()

    model_df = model_df.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    model_df = model_df.dropna()

    if len(model_df) < 50:
        raise ValueError(
            f"Not enough usable rows for ML: {len(model_df)}"
        )

    X = model_df[feature_columns]
    y = model_df["sales_revenue"]

    # Time-based split.
    split_index = int(len(model_df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=6,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    )

    importance = importance.sort_values(
        "importance",
        ascending=False,
    )

    importance["importance_pct"] = (
        importance["importance"]
        / importance["importance"].sum()
        * 100
    )

    output = Path(OUTPUT_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)
    importance.to_csv(output, index=False)

    print("\n=== Narrate IQ ML Driver Model ===\n")

    print(f"Usable rows:  {len(model_df)}")
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows:  {len(X_test)}")

    print("\nModel performance:")
    print(f"MAE: ${mae:,.2f}")
    print(f"R²:  {r2:.4f}")

    print("\nTop ML drivers:")

    print(
        importance[
            ["feature", "importance_pct"]
        ]
        .head(15)
        .to_string(index=False)
    )

    print(f"\nSaved to: {output}")


if __name__ == "__main__":
    train_model()