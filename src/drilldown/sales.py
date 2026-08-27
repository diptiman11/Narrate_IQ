from pathlib import Path

import pandas as pd


SALES_PATH = Path("data/raw/sales.csv")
OUTPUT_DIR = Path("data/processed")


def _aggregate_dimension(
    current: pd.DataFrame,
    previous: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:

    current_group = (
        current.groupby(dimension, dropna=False)
        .agg(
            current_units=("units", "sum"),
            current_revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    previous_group = (
        previous.groupby(dimension, dropna=False)
        .agg(
            previous_units=("units", "sum"),
            previous_revenue=("revenue", "sum"),
        )
        .reset_index()
    )

    result = current_group.merge(
        previous_group,
        on=dimension,
        how="outer",
    )

    numeric_columns = [
        "current_units",
        "current_revenue",
        "previous_units",
        "previous_revenue",
    ]

    for column in numeric_columns:
        result[column] = result[column].fillna(0)

    result["unit_change"] = (
        result["current_units"]
        - result["previous_units"]
    )

    result["revenue_change"] = (
        result["current_revenue"]
        - result["previous_revenue"]
    )

    result["unit_change_pct"] = (
        result["unit_change"]
        / result["previous_units"].abs().replace(0, pd.NA)
        * 100
    )

    result["revenue_change_pct"] = (
        result["revenue_change"]
        / result["previous_revenue"].abs().replace(0, pd.NA)
        * 100
    )

    result["dimension"] = dimension

    return result[
        [
            "dimension",
            dimension,
            "current_units",
            "previous_units",
            "unit_change",
            "unit_change_pct",
            "current_revenue",
            "previous_revenue",
            "revenue_change",
            "revenue_change_pct",
        ]
    ]


def generate_sales_drilldown() -> pd.DataFrame:

    sales = pd.read_csv(SALES_PATH)

    sales["date"] = pd.to_datetime(
        sales["date"]
    )

    latest_date = sales["date"].max()

    current_start = latest_date
    current_end = latest_date

    previous_start = (
        latest_date - pd.Timedelta(days=7)
    )
    previous_end = (
        latest_date - pd.Timedelta(days=1)
    )

    current = sales[
        (sales["date"] >= current_start)
        & (sales["date"] <= current_end)
    ].copy()

    previous = sales[
        (sales["date"] >= previous_start)
        & (sales["date"] <= previous_end)
    ].copy()

    # Compare latest day with the previous 7-day period
    dimensions = [
        "region",
        "product_id",
        "product_name",
        "category",
        "channel",
    ]

    results = []

    for dimension in dimensions:

        result = _aggregate_dimension(
            current=current,
            previous=previous,
            dimension=dimension,
        )

        results.append(result)

    final = pd.concat(
        results,
        ignore_index=True,
    )

    final["date"] = latest_date

    final = final.sort_values(
        "unit_change"
    )

    return final


def main() -> None:

    result = generate_sales_drilldown()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / "sales_dimension_drilldown.csv"
    )

    result.to_csv(
        output_path,
        index=False,
    )

    print(
        "\n=== Narrate IQ Sales Drilldown ===\n"
    )

    print(
        result.head(20).to_string(
            index=False
        )
    )

    print(
        f"\nSaved to: {output_path}"
    )


if __name__ == "__main__":
    main()
