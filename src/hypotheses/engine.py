from pathlib import Path

import pandas as pd


KPI_PATH = "data/processed/daily_kpis.csv"
ATTRIBUTION_PATH = "data/processed/driver_attribution.csv"
CONFIDENCE_PATH = "data/processed/confidence_scores.csv"
VALIDATION_PATH = "data/processed/evidence_validation.csv"
HISTORY_PATH = "data/processed/hypothesis_history.csv"

OUTPUT_PATH = "data/processed/hypotheses.csv"


def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.50:
        return "medium"
    return "low"


def _historical_reliability(
    hypothesis: str,
    history: pd.DataFrame,
) -> float:
    if history.empty:
        return 0.0

    match = history[
        history["hypothesis"] == hypothesis
    ]

    if match.empty:
        return 0.0

    return float(
        match.iloc[0]["historical_reliability"]
    )


def _combined_score(
    current_confidence: float,
    validation_score: float,
    historical_reliability: float,
) -> float:
    """
    Current evidence is weighted most heavily.
    Historical reliability provides a smaller learning signal.
    """

    score = (
        0.45 * current_confidence
        + 0.40 * validation_score
        + 0.15 * historical_reliability
    )

    return round(
        min(max(score, 0.0), 1.0),
        2,
    )


def generate_hypotheses() -> pd.DataFrame:
    kpis = pd.read_csv(KPI_PATH)
    attribution = pd.read_csv(ATTRIBUTION_PATH)
    confidence = pd.read_csv(CONFIDENCE_PATH)
    validation = pd.read_csv(VALIDATION_PATH)

    if Path(HISTORY_PATH).exists():
        history = pd.read_csv(HISTORY_PATH)
    else:
        history = pd.DataFrame()

    if kpis.empty:
        return pd.DataFrame()

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

    latest_validation = validation[
        validation["date"] == latest_date
    ].copy()

    revenue_wow = (
        float(latest_kpi["revenue_wow_pct"])
        * 100
    )

    hypotheses = []

    def add_hypothesis(
        hypothesis_name: str,
        base_score: float,
        evidence: str,
    ) -> None:

        validation_match = latest_validation[
            latest_validation["hypothesis"]
            == hypothesis_name
        ]

        validation_score = (
            float(
                validation_match.iloc[0][
                    "validation_score"
                ]
            )
            if not validation_match.empty
            else 0.0
        )

        historical = _historical_reliability(
            hypothesis_name,
            history,
        )

        score = _combined_score(
            current_confidence=base_score,
            validation_score=validation_score,
            historical_reliability=historical,
        )

        if score >= 0.75:
            status = "strongly_supported"
        elif score >= 0.40:
            status = "supported"
        elif score > 0:
            status = "weakly_supported"
        else:
            status = "unsupported"

        hypotheses.append(
            {
                "date": latest_date,
                "hypothesis": hypothesis_name,
                "base_confidence_score": round(
                    base_score,
                    2,
                ),
                "validation_score": round(
                    validation_score,
                    2,
                ),
                "historical_reliability": round(
                    historical,
                    2,
                ),
                "confidence_score": score,
                "confidence": _confidence_label(score),
                "status": status,
                "revenue_change_pct": revenue_wow,
                "evidence": evidence,
            }
        )

    # ---------------------------------------------
    # Sales volume deterioration
    # ---------------------------------------------

    sales_units = latest_attr[
        latest_attr["driver"] == "sales_units"
    ]

    if not sales_units.empty:

        row = sales_units.iloc[0]

        change = float(
            row["driver_change_pct"]
        )

        importance = float(
            row["model_importance_pct"]
        )

        if change < -2:

            confidence_match = latest_conf[
                latest_conf["driver"]
                == "sales_units"
            ]

            base_score = (
                float(
                    confidence_match.iloc[0][
                        "confidence_score"
                    ]
                )
                if not confidence_match.empty
                else 0.0
            )

            add_hypothesis(
                "Sales volume deterioration",
                base_score,
                (
                    f"sales units changed "
                    f"{change:+.2f}%; "
                    f"ML importance "
                    f"{importance:.2f}%"
                ),
            )

    # ---------------------------------------------
    # Inventory constraint
    # ---------------------------------------------

    stockout = latest_attr[
        latest_attr["driver"]
        == "stockout_hours"
    ]

    closing_stock = latest_attr[
        latest_attr["driver"]
        == "closing_stock"
    ]

    if not stockout.empty and not closing_stock.empty:

        stockout_change = float(
            stockout.iloc[0][
                "driver_change_pct"
            ]
        )

        stock_change = float(
            closing_stock.iloc[0][
                "driver_change_pct"
            ]
        )

        if (
            stockout_change > 5
            or stock_change < -5
        ):

            confidence_match = latest_conf[
                latest_conf["driver"].isin(
                    [
                        "stockout_hours",
                        "closing_stock",
                    ]
                )
            ]

            base_score = (
                float(
                    confidence_match[
                        "confidence_score"
                    ].max()
                )
                if not confidence_match.empty
                else 0.0
            )

            add_hypothesis(
                "Inventory constraint",
                base_score,
                (
                    f"stockout hours changed "
                    f"{stockout_change:+.2f}%; "
                    f"closing stock changed "
                    f"{stock_change:+.2f}%"
                ),
            )

    # ---------------------------------------------
    # Marketing efficiency deterioration
    # ---------------------------------------------

    marketing = latest_attr[
        latest_attr["driver"]
        == "marketing_conversion_rate"
    ]

    if not marketing.empty:

        change = float(
            marketing.iloc[0][
                "driver_change_pct"
            ]
        )

        if change < -5:

            confidence_match = latest_conf[
                latest_conf["driver"]
                == "marketing_conversion_rate"
            ]

            base_score = (
                float(
                    confidence_match.iloc[0][
                        "confidence_score"
                    ]
                )
                if not confidence_match.empty
                else 0.0
            )

            add_hypothesis(
                "Marketing efficiency deterioration",
                base_score,
                (
                    f"marketing conversion rate "
                    f"changed {change:+.2f}%"
                ),
            )

    result = pd.DataFrame(hypotheses)

    if not result.empty:

        result = result.sort_values(
            "confidence_score",
            ascending=False,
        ).reset_index(drop=True)

        result["hypothesis_rank"] = (
            result.index + 1
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
        "\n=== Narrate IQ Learning-Aware "
        "Hypothesis Engine ===\n"
    )

    if result.empty:
        print("No hypotheses generated.")
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
