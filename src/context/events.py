from pathlib import Path

import pandas as pd


EVENTS_PATH = Path(
    "data/raw/business_events.csv"
)

KPI_PATH = Path(
    "data/processed/daily_kpis.csv"
)

OUTPUT_PATH = Path(
    "data/processed/event_context.csv"
)


def classify_event(event_type: str) -> str:
    mapping = {
        "marketing": "marketing",
        "supply": "inventory",
        "external": "competitive",
    }

    return mapping.get(
        str(event_type).lower(),
        "other",
    )


def generate_event_context() -> pd.DataFrame:
    events = pd.read_csv(EVENTS_PATH)
    kpis = pd.read_csv(KPI_PATH)

    if events.empty or kpis.empty:
        return pd.DataFrame()

    events["event_date"] = pd.to_datetime(
        events["event_date"]
    )

    kpis["date"] = pd.to_datetime(
        kpis["date"]
    )

    kpis = kpis.sort_values("date")

    results = []

    for _, event in events.iterrows():

        event_date = event["event_date"]

        same_day = kpis[
            kpis["date"] == event_date
        ]

        if same_day.empty:
            continue

        current = same_day.iloc[0]

        before = kpis[
            kpis["date"] < event_date
        ].tail(7)

        if before.empty:
            revenue_change_pct = None
            units_change_pct = None
        else:
            revenue_baseline = before[
                "revenue"
            ].mean()

            units_baseline = before[
                "units_sold"
            ].mean()

            revenue_change_pct = (
                (
                    float(current["revenue"])
                    - revenue_baseline
                )
                / abs(revenue_baseline)
                * 100
                if revenue_baseline != 0
                else None
            )

            units_change_pct = (
                (
                    float(current["units_sold"])
                    - units_baseline
                )
                / abs(units_baseline)
                * 100
                if units_baseline != 0
                else None
            )

        results.append(
            {
                "event_date": event_date.strftime(
                    "%Y-%m-%d"
                ),
                "event_name": event["event_name"],
                "event_type": event["event_type"],
                "event_category": classify_event(
                    event["event_type"]
                ),
                "description": event["description"],
                "revenue_change_vs_prior_7d_pct": (
                    revenue_change_pct
                ),
                "units_change_vs_prior_7d_pct": (
                    units_change_pct
                ),
            }
        )

    return pd.DataFrame(results)


def main() -> None:
    result = generate_event_context()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "\n=== Narrate IQ Business Event Context ===\n"
    )

    if result.empty:
        print("No event context generated.")
    else:
        print(
            result.to_string(index=False)
        )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
