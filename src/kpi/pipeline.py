from pathlib import Path

from src.ingestion.loaders import load_all_sources

from .calculations import calculate_daily_kpis
from .materiality import add_materiality_flags
from .movements import add_movement_metrics


OUTPUT_PATH = Path("data/processed/daily_kpis.csv")


def run_kpi_pipeline():

    print("\n=== Narrate IQ KPI Engine ===\n")

    print("Loading validated sources...")

    datasets = load_all_sources()

    sales = datasets["sales"]
    marketing = datasets["marketing"]
    inventory = datasets["inventory"]

    print("Calculating daily KPIs...")

    kpis = calculate_daily_kpis(
        sales=sales,
        marketing=marketing,
        inventory=inventory,
    )

    print("Calculating temporal movements...")

    kpis = add_movement_metrics(kpis)

    print("Calculating materiality...")

    kpis = add_materiality_flags(kpis)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    kpis.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved KPI dataset to: {OUTPUT_PATH}"
    )

    print(
        f"Rows: {len(kpis):,}"
    )

    print(
        f"Columns: {len(kpis.columns):,}"
    )

    print("\nLatest KPI snapshot:\n")

    latest = kpis.iloc[-1]

    metrics = [
        "revenue",
        "units_sold",
        "average_selling_price",
        "marketing_spend",
        "conversion_rate",
        "stockout_rate",
    ]

    for metric in metrics:

        print(
            f"{metric:25} "
            f"{latest[metric]:,.4f}"
        )

    print("\nLatest WoW movements:\n")

    for metric in metrics:

        value = latest[f"{metric}_wow_pct"]

        if value != value:
            formatted = "N/A"
        else:
            formatted = f"{value:+.2%}"

        print(
            f"{metric:25} "
            f"{formatted}"
        )


if __name__ == "__main__":
    run_kpi_pipeline()