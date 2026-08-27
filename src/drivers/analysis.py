from pathlib import Path

import pandas as pd


def calculate_revenue_drivers(
    kpi_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Decompose revenue movement into volume and price effects.

    Revenue = Units Sold × Average Selling Price
    """

    required = [
        "date",
        "revenue",
        "units_sold",
        "average_selling_price",
        "revenue_wow_pct",
        "units_sold_wow_pct",
        "average_selling_price_wow_pct",
    ]

    missing = [column for column in required if column not in kpi_df.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = kpi_df.copy()

    df["previous_revenue"] = df["revenue"].shift(7)
    df["previous_units"] = df["units_sold"].shift(7)
    df["previous_asp"] = df["average_selling_price"].shift(7)

    # Revenue impact caused by volume change while holding price constant.
    df["volume_effect"] = (
        (df["units_sold"] - df["previous_units"])
        * df["previous_asp"]
    )

    # Revenue impact caused by price change while holding volume constant.
    df["price_effect"] = (
        (df["average_selling_price"] - df["previous_asp"])
        * df["units_sold"]
    )

    df["revenue_change"] = (
        df["revenue"] - df["previous_revenue"]
    )

    # Contribution percentages.
    denominator = df["volume_effect"].abs() + df["price_effect"].abs()

    df["volume_contribution_pct"] = (
        df["volume_effect"].abs() / denominator * 100
    ).where(denominator != 0)

    df["price_contribution_pct"] = (
        df["price_effect"].abs() / denominator * 100
    ).where(denominator != 0)

    return df[
        [
            "date",
            "revenue",
            "revenue_change",
            "revenue_wow_pct",
            "units_sold",
            "units_sold_wow_pct",
            "average_selling_price",
            "average_selling_price_wow_pct",
            "volume_effect",
            "price_effect",
            "volume_contribution_pct",
            "price_contribution_pct",
        ]
    ]


def main() -> None:
    input_path = Path("data/processed/daily_kpis.csv")
    output_path = Path("data/processed/revenue_drivers.csv")

    if not input_path.exists():
        raise FileNotFoundError(
            f"KPI dataset not found: {input_path}"
        )

    kpi_df = pd.read_csv(input_path)

    result = calculate_revenue_drivers(kpi_df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    print("\n=== Narrate IQ Revenue Driver Analysis ===\n")
    print(f"Input rows: {len(kpi_df)}")
    print(f"Output rows: {len(result)}")
    print(f"Saved to: {output_path}")

    print("\nLatest driver analysis:")

    print(
        result.tail(7).to_string(index=False)
    )


if __name__ == "__main__":
    main()