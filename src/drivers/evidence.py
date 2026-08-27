from pathlib import Path

import pandas as pd


def build_driver_evidence() -> pd.DataFrame:
    sales = pd.read_csv("data/raw/sales.csv")
    marketing = pd.read_csv("data/raw/marketing.csv")
    inventory = pd.read_csv("data/raw/inventory.csv")

    sales["date"] = pd.to_datetime(sales["date"])
    marketing["date"] = pd.to_datetime(marketing["date"])
    inventory["date"] = pd.to_datetime(inventory["date"])

    daily_sales = (
        sales.groupby("date")
        .agg(
            sales_units=("units", "sum"),
            sales_revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    daily_marketing = (
        marketing.groupby("date")
        .agg(
            marketing_spend=("spend", "sum"),
            marketing_clicks=("clicks", "sum"),
            marketing_conversions=("conversions", "sum"),
        )
        .reset_index()
    )

    daily_inventory = (
        inventory.groupby("date")
        .agg(
            stockout_hours=("stockout_hours", "sum"),
            inventory_units_sold=("units_sold", "sum"),
            closing_stock=("closing_stock", "sum"),
        )
        .reset_index()
    )

    evidence = daily_sales.merge(
        daily_marketing,
        on="date",
        how="left",
    ).merge(
        daily_inventory,
        on="date",
        how="left",
    )

    evidence["marketing_conversion_rate"] = (
        evidence["marketing_conversions"]
        / evidence["marketing_clicks"]
    ).where(
        evidence["marketing_clicks"] > 0
    )

    return evidence


def main() -> None:
    output_path = Path("data/processed/driver_evidence.csv")

    evidence = build_driver_evidence()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    evidence.to_csv(output_path, index=False)

    print("\n=== Narrate IQ Driver Evidence ===\n")
    print(f"Rows: {len(evidence)}")
    print(f"Columns: {len(evidence.columns)}")
    print(f"Saved to: {output_path}")

    print("\nLatest evidence:")
    print(evidence.tail(7).to_string(index=False))


if __name__ == "__main__":
    main()