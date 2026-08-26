import pandas as pd


def add_movement_metrics(
    kpis: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add temporal movement metrics to the daily KPI table.

    Metrics:
    - day-over-day percentage change
    - week-over-week percentage change
    - 7-day rolling mean
    - 28-day rolling mean
    - 28-day rolling standard deviation
    """

    df = kpis.copy()

    df = df.sort_values("date").reset_index(drop=True)

    metric_columns = [
        "revenue",
        "units_sold",
        "average_selling_price",
        "marketing_spend",
        "conversion_rate",
        "stockout_rate",
    ]

    for metric in metric_columns:

        # Day-over-day
        df[f"{metric}_dod_pct"] = (
            df[metric].pct_change()
        )

        # Week-over-week
        df[f"{metric}_wow_pct"] = (
            df[metric].pct_change(periods=7)
        )

        # Rolling baseline
        df[f"{metric}_rolling_7d"] = (
            df[metric]
            .rolling(window=7, min_periods=7)
            .mean()
        )

        df[f"{metric}_rolling_28d"] = (
            df[metric]
            .rolling(window=28, min_periods=28)
            .mean()
        )

        df[f"{metric}_rolling_28d_std"] = (
            df[metric]
            .rolling(window=28, min_periods=28)
            .std()
        )

        # Standardized deviation from 28-day baseline
        df[f"{metric}_zscore"] = (
            (
                df[metric]
                - df[f"{metric}_rolling_28d"]
            )
            / df[f"{metric}_rolling_28d_std"]
        )
        df = df.replace(
        [float("inf"), float("-inf")],
        float("nan"),
    )

    return df