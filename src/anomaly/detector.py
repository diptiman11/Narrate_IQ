from pathlib import Path

import pandas as pd


KPI_CONFIG = {
    "revenue": {
        "zscore": "revenue_zscore",
        "movement": "revenue_wow_pct",
        "materiality": "revenue_materiality",
    },
    "units_sold": {
        "zscore": "units_sold_zscore",
        "movement": "units_sold_wow_pct",
        "materiality": "units_sold_materiality",
    },
    "average_selling_price": {
        "zscore": "average_selling_price_zscore",
        "movement": "average_selling_price_wow_pct",
        "materiality": "average_selling_price_materiality",
    },
    "marketing_spend": {
        "zscore": "marketing_spend_zscore",
        "movement": "marketing_spend_wow_pct",
        "materiality": "marketing_spend_materiality",
    },
    "conversion_rate": {
        "zscore": "conversion_rate_zscore",
        "movement": "conversion_rate_wow_pct",
        "materiality": "conversion_rate_materiality",
    },
    "stockout_rate": {
        "zscore": "stockout_rate_zscore",
        "movement": "stockout_rate_wow_pct",
        "materiality": "stockout_rate_materiality",
    },
}


def detect_anomalies(
    kpi_df: pd.DataFrame,
    zscore_threshold: float = 2.0,
) -> pd.DataFrame:
    """
    Detect KPI anomalies using the z-score and materiality
    features already produced by the KPI engine.
    """

    anomalies = []

    for kpi, config in KPI_CONFIG.items():
        required_columns = [
            "date",
            kpi,
            config["zscore"],
            config["movement"],
            config["materiality"],
        ]

        missing = [
            column
            for column in required_columns
            if column not in kpi_df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing columns for {kpi}: {missing}"
            )

        for _, row in kpi_df.iterrows():
            zscore = row[config["zscore"]]

            if pd.isna(zscore):
                continue

            materiality = row[config["materiality"]]

            if abs(zscore) >= zscore_threshold or materiality == "high":
                anomalies.append(
                    {
                        "date": row["date"],
                        "kpi": kpi,
                        "value": row[kpi],
                        "z_score": zscore,
                        "wow_change_pct": row[config["movement"]],
                        "materiality": materiality,
                        "direction": (
                            "increase"
                            if zscore > 0
                            else "decrease"
                        ),
                    }
                )

    return pd.DataFrame(anomalies)


def main() -> None:
    input_path = Path("data/processed/daily_kpis.csv")
    output_path = Path("data/processed/anomalies.csv")

    if not input_path.exists():
        raise FileNotFoundError(
            f"KPI dataset not found: {input_path}"
        )

    df = pd.read_csv(input_path)

    anomalies = detect_anomalies(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    anomalies.to_csv(output_path, index=False)

    print("\n=== Narrate IQ Anomaly Detector ===\n")
    print(f"Input rows: {len(df)}")
    print(f"Anomalies detected: {len(anomalies)}")
    print(f"Saved to: {output_path}")

    if not anomalies.empty:
        print("\nLatest anomalies:")
        print(
            anomalies
            .sort_values("date")
            .tail(10)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()