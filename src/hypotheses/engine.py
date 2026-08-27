from pathlib import Path

import pandas as pd


KPI_PATH = "data/processed/daily_kpis.csv"
ATTRIBUTION_PATH = "data/processed/driver_attribution.csv"
CONFIDENCE_PATH = "data/processed/confidence_scores.csv"

OUTPUT_PATH = "data/processed/hypotheses.csv"


def generate_hypotheses() -> pd.DataFrame:
    kpis = pd.read_csv(KPI_PATH)
    attribution = pd.read_csv(ATTRIBUTION_PATH)
    confidence = pd.read_csv(CONFIDENCE_PATH)

    latest_date = kpis["date"].max()

    latest_kpi = kpis[
        kpis["date"] == latest_date
    ].iloc[0]

    latest_attr = attribution[
        attribution["date"] == latest_date
    ].copy()

    latest_conf = confidence[
        confidence["date"] == latest_date
    ].copy()

    revenue_wow = float(
        latest_kpi["revenue_wow_pct"]
    ) * 100

    hypotheses = []

    # Hypothesis 1: volume deterioration
    sales_units = latest_attr[
        latest_attr["driver"] == "sales_units"
    ]

    if not sales_units.empty:
        row = sales_units.iloc[0]

        change = float(row["driver_change_pct"])
        importance = float(row["model_importance_pct"])

        if change < -2:
            confidence_match = latest_conf[
                latest_conf["driver"] == "sales_units"
            ]

            confidence_score = (
                float(
                    confidence_match.iloc[0][
                        "confidence_score"
                    ]
                )
                if not confidence_match.empty
                else 0.0
            )

            evidence = [
                f"sales units changed {change:+.2f}%",
                f"ML importance {importance:.2f}%",
            ]

            hypotheses.append(
                {
                    "date": latest_date,
                    "hypothesis": "Sales volume deterioration",
                    "status": "supported",
                    "confidence_score": confidence_score,
                    "confidence": (
                        confidence_match.iloc[0]["confidence"]
                        if not confidence_match.empty
                        else "low"
                    ),
                    "revenue_change_pct": revenue_wow,
                    "evidence": "; ".join(evidence),
                }
            )

    # Hypothesis 2: inventory constraint
    stockout = latest_attr[
        latest_attr["driver"] == "stockout_hours"
    ]

    closing_stock = latest_attr[
        latest_attr["driver"] == "closing_stock"
    ]

    if not stockout.empty and not closing_stock.empty:

        stockout_change = float(
            stockout.iloc[0]["driver_change_pct"]
        )

        stock_change = float(
            closing_stock.iloc[0]["driver_change_pct"]
        )

        if stockout_change > 5 or stock_change < -5:

            confidence_match = latest_conf[
                latest_conf["driver"].isin(
                    ["stockout_hours", "closing_stock"]
                )
            ]

            scores = (
                confidence_match["confidence_score"]
                if not confidence_match.empty
                else pd.Series(dtype=float)
            )

            confidence_score = (
                float(scores.max())
                if not scores.empty
                else 0.0
            )

            evidence = [
                f"stockout hours changed {stockout_change:+.2f}%",
                f"closing stock changed {stock_change:+.2f}%",
            ]

            hypotheses.append(
                {
                    "date": latest_date,
                    "hypothesis": "Inventory constraint",
                    "status": "supported",
                    "confidence_score": confidence_score,
                    "confidence": (
                        "high"
                        if confidence_score >= 0.75
                        else "medium"
                        if confidence_score >= 0.50
                        else "low"
                    ),
                    "revenue_change_pct": revenue_wow,
                    "evidence": "; ".join(evidence),
                }
            )

    # Hypothesis 3: marketing efficiency deterioration
    marketing = latest_attr[
        latest_attr["driver"]
        == "marketing_conversion_rate"
    ]

    if not marketing.empty:

        change = float(
            marketing.iloc[0]["driver_change_pct"]
        )

        if change < -5:

            confidence_match = latest_conf[
                latest_conf["driver"]
                == "marketing_conversion_rate"
            ]

            confidence_score = (
                float(
                    confidence_match.iloc[0][
                        "confidence_score"
                    ]
                )
                if not confidence_match.empty
                else 0.0
            )

            hypotheses.append(
                {
                    "date": latest_date,
                    "hypothesis": (
                        "Marketing efficiency deterioration"
                    ),
                    "status": "supported",
                    "confidence_score": confidence_score,
                    "confidence": (
                        confidence_match.iloc[0]["confidence"]
                        if not confidence_match.empty
                        else "low"
                    ),
                    "revenue_change_pct": revenue_wow,
                    "evidence": (
                        f"marketing conversion rate changed "
                        f"{change:+.2f}%"
                    ),
                }
            )

    result = pd.DataFrame(hypotheses)

    if not result.empty:
        result = result.sort_values(
            "confidence_score",
            ascending=False,
        )

    output = Path(OUTPUT_PATH)
    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        output,
        index=False,
    )

    return result


def main() -> None:
    result = generate_hypotheses()

    print(
        "\n=== Narrate IQ Hypothesis Engine ===\n"
    )

    if result.empty:
        print("No supported hypotheses generated.")
    else:
        print(
            result.to_string(index=False)
        )

    print(
        "\nSaved to: "
        "data/processed/hypotheses.csv"
    )


if __name__ == "__main__":
    main()