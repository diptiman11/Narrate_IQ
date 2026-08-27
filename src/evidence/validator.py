from pathlib import Path

import pandas as pd


BASE_DIR = Path("data/processed")

HYPOTHESES_PATH = BASE_DIR / "hypotheses.csv"
ATTRIBUTION_PATH = BASE_DIR / "driver_attribution.csv"
ANOMALIES_PATH = BASE_DIR / "anomalies.csv"

OUTPUT_PATH = BASE_DIR / "evidence_validation.csv"


def _score_hypothesis(
    hypothesis_name: str,
    attribution: pd.DataFrame,
) -> tuple[float, list[str], list[str]]:
    """
    Score one hypothesis using supporting and contradicting evidence.

    Returns:
        score,
        supporting_evidence,
        contradicting_evidence
    """

    score = 0.0
    supporting = []
    contradicting = []

    if hypothesis_name == "Sales volume deterioration":
        rows = attribution[
            attribution["driver"] == "sales_units"
        ]

        if not rows.empty:
            row = rows.iloc[0]

            change = float(row["driver_change_pct"])
            importance = float(row["model_importance_pct"])

            supporting.append(
                f"sales_units changed {change:+.2f}%"
            )

            supporting.append(
                f"ML importance {importance:.2f}%"
            )

            if change < 0:
                score += 0.40
            else:
                contradicting.append(
                    f"sales_units changed {change:+.2f}%"
                )

            if importance >= 50:
                score += 0.40
            elif importance >= 10:
                score += 0.20
            else:
                contradicting.append(
                    f"ML importance only {importance:.2f}%"
                )

    elif hypothesis_name == "Inventory constraint":
        stockout = attribution[
            attribution["driver"] == "stockout_hours"
        ]

        closing_stock = attribution[
            attribution["driver"] == "closing_stock"
        ]

        if not stockout.empty:
            change = float(
                stockout.iloc[0]["driver_change_pct"]
            )

            if change > 0:
                score += 0.25
                supporting.append(
                    f"stockout_hours changed {change:+.2f}%"
                )
            else:
                contradicting.append(
                    f"stockout_hours changed {change:+.2f}%"
                )

        if not closing_stock.empty:
            change = float(
                closing_stock.iloc[0]["driver_change_pct"]
            )

            if change < 0:
                score += 0.25
                supporting.append(
                    f"closing_stock changed {change:+.2f}%"
                )
            else:
                contradicting.append(
                    f"closing_stock changed {change:+.2f}%"
                )

    elif (
        hypothesis_name
        == "Marketing efficiency deterioration"
    ):
        conversion = attribution[
            attribution["driver"]
            == "marketing_conversion_rate"
        ]

        if not conversion.empty:
            change = float(
                conversion.iloc[0]["driver_change_pct"]
            )

            if change < 0:
                score += 0.40
                supporting.append(
                    "marketing_conversion_rate "
                    f"changed {change:+.2f}%"
                )
            else:
                contradicting.append(
                    "marketing_conversion_rate "
                    f"changed {change:+.2f}%"
                )

        spend = attribution[
            attribution["driver"] == "marketing_spend"
        ]

        if not spend.empty:
            spend_change = float(
                spend.iloc[0]["driver_change_pct"]
            )

            supporting.append(
                f"marketing_spend changed "
                f"{spend_change:+.2f}%"
            )

            if spend_change > 0:
                score += 0.10

    return score, supporting, contradicting


def validate_hypotheses() -> pd.DataFrame:
    hypotheses = pd.read_csv(HYPOTHESES_PATH)
    attribution = pd.read_csv(ATTRIBUTION_PATH)
    anomalies = pd.read_csv(ANOMALIES_PATH)

    if hypotheses.empty:
        return pd.DataFrame()

    latest_date = hypotheses["date"].max()

    hypotheses = hypotheses[
        hypotheses["date"] == latest_date
    ].copy()

    attribution = attribution[
        attribution["date"] == latest_date
    ].copy()

    anomalies = anomalies[
        anomalies["date"] == latest_date
    ].copy()

    results = []

    for _, hypothesis in hypotheses.iterrows():
        name = hypothesis["hypothesis"]

        score, supporting, contradicting = (
            _score_hypothesis(
                name,
                attribution,
            )
        )

        if score >= 0.70:
            status = "strongly_supported"
        elif score >= 0.40:
            status = "supported"
        elif score > 0:
            status = "weakly_supported"
        else:
            status = "unsupported"

        results.append(
            {
                "date": latest_date,
                "hypothesis": name,
                "validation_score": round(score, 2),
                "status": status,
                "supporting_evidence": "; ".join(
                    supporting
                ),
                "contradicting_evidence": "; ".join(
                    contradicting
                ),
                "anomaly_count": len(anomalies),
            }
        )

    result = pd.DataFrame(results)

    if not result.empty:
        result = result.sort_values(
            by="validation_score",
            ascending=False,
        ).reset_index(drop=True)

        result["validation_rank"] = (
            result.index + 1
        )

    return result


def main() -> None:
    result = validate_hypotheses()

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "\n=== Narrate IQ Evidence Validation ===\n"
    )

    print(result.to_string(index=False))

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()