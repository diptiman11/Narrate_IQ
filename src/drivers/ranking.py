from pathlib import Path

import pandas as pd


def rank_revenue_drivers() -> pd.DataFrame:
    drivers = pd.read_csv("data/processed/revenue_drivers.csv")
    evidence = pd.read_csv("data/processed/driver_evidence.csv")

    drivers["date"] = pd.to_datetime(drivers["date"])
    evidence["date"] = pd.to_datetime(evidence["date"])

    df = drivers.merge(
        evidence,
        on="date",
        how="left",
    )

    df["volume_score"] = df["volume_contribution_pct"].fillna(0)
    df["price_score"] = df["price_contribution_pct"].fillna(0)

    marketing_change = df["marketing_spend"].pct_change(7).abs() * 100
    inventory_change = df["stockout_hours"].pct_change(7).abs() * 100

    df["marketing_score"] = marketing_change.fillna(0)
    df["inventory_score"] = inventory_change.fillna(0)

    score_columns = [
        "volume_score",
        "price_score",
        "marketing_score",
        "inventory_score",
    ]

    df["primary_driver"] = (
        df[score_columns]
        .fillna(0)
        .idxmax(axis=1)
        .str.replace("_score", "", regex=False)
    )

    return df[
        [
            "date",
            "revenue",
            "revenue_change",
            "revenue_wow_pct",
            "volume_effect",
            "price_effect",
            "volume_contribution_pct",
            "price_contribution_pct",
            "marketing_spend",
            "marketing_conversion_rate",
            "stockout_hours",
            "closing_stock",
            "primary_driver",
        ]
    ]


def main() -> None:
    output_path = Path("data/processed/revenue_driver_ranking.csv")

    result = rank_revenue_drivers()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    print("\n=== Narrate IQ Revenue Driver Ranking ===\n")
    print(f"Rows: {len(result)}")
    print(f"Saved to: {output_path}")

    print("\nLatest driver ranking:")
    print(result.tail(7).to_string(index=False))


if __name__ == "__main__":
    main()
