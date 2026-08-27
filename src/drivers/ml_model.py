from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


INPUT_PATH = "data/processed/driver_evidence.csv"
OUTPUT_PATH = "data/processed/ml_driver_importance.csv"


FEATURES = [
    "sales_units",
    "marketing_spend",
    "marketing_clicks",
    "marketing_conversions",
    "marketing_conversion_rate",
    "stockout_hours",
    "closing_stock",
]

TARGET = "sales_revenue"


def train_model():

    df = pd.read_csv(INPUT_PATH)

    df["date"] = pd.to_datetime(df["date"])

    # Keep only columns required by the model.
    model_df = df[["date", *FEATURES, TARGET]].copy()

    # Replace infinite values with missing values.
    model_df = model_df.replace([float("inf"), float("-inf")], pd.NA)

    # Remove rows where required model data is unavailable.
    model_df = model_df.dropna()

    if len(model_df) < 30:
        raise ValueError(
            f"Not enough usable rows for ML training: {len(model_df)}"
        )

    X = model_df[FEATURES]
    y = model_df[TARGET]

    # Time-aware split: don't randomly mix future and past.
    split_index = int(len(model_df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=8,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance": model.feature_importances_,
        }
    ).sort_values(
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

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows:  {len(X_test)}")

    print("\nModel performance:")
    print(f"MAE: ${mae:,.2f}")
    print(f"R²:  {r2:.4f}")

    print("\nFeature importance:")
    print(
        importance[
            ["feature", "importance_pct"]
        ].to_string(index=False)
    )

    print(f"\nSaved to: {output}")


if __name__ == "__main__":
    train_model()