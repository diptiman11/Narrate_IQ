import pandas as pd


DEFAULT_THRESHOLDS = {
    "revenue": 0.05,
    "units_sold": 0.08,
    "average_selling_price": 0.05,
    "marketing_spend": 0.10,
    "conversion_rate": 0.05,
    "stockout_rate": 0.03,
}


def classify_materiality(
    value: float,
    threshold: float,
) -> str:
    """
    Classify a movement based on absolute percentage change.
    """

    if pd.isna(value):
        return "insufficient_history"

    magnitude = abs(value)

    if magnitude >= threshold * 2:
        return "high"

    if magnitude >= threshold:
        return "medium"

    return "low"


def add_materiality_flags(
    kpis: pd.DataFrame,
) -> pd.DataFrame:

    df = kpis.copy()

    for metric, threshold in DEFAULT_THRESHOLDS.items():

        column = f"{metric}_wow_pct"

        df[f"{metric}_materiality"] = df[column].apply(
            lambda value: classify_materiality(
                value,
                threshold,
            )
        )

    return df