from pathlib import Path

import pandas as pd


BASE_DIR = Path("data/processed")

HYPOTHESES_PATH = BASE_DIR / "hypotheses.csv"
ATTRIBUTION_PATH = BASE_DIR / "driver_attribution.csv"
ANOMALIES_PATH = BASE_DIR / "anomalies.csv"
EVENT_CONTEXT_PATH = BASE_DIR / "event_context.csv"
DRILLDOWN_PATH = BASE_DIR / "sales_dimension_drilldown.csv"

OUTPUT_PATH = BASE_DIR / "evidence_validation.csv"


def _score_hypothesis(
    hypothesis_name: str,
    attribution: pd.DataFrame,
) -> tuple[float, list[str], list[str]]:

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
            importance = float(
                row["model_importance_pct"]
            )

            if change < 0:
                score += 0.40
                supporting.append(
                    f"sales_units changed {change:+.2f}%"
                )
            else:
                contradicting.append(
                    f"sales_units changed {change:+.2f}%"
                )

            if importance >= 50:
                score += 0.40
                supporting.append(
                    f"ML importance {importance:.2f}%"
                )
            elif importance >= 10:
                score += 0.20
                supporting.append(
                    f"ML importance {importance:.2f}%"
                )
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


def _score_segment_evidence(
    drilldown: pd.DataFrame,
) -> tuple[float, list[str]]:

    if drilldown.empty:
        return 0.0, []

    subset = drilldown[
        drilldown["unit_change"] < 0
    ].copy()

    if subset.empty:
        return 0.0, []

    # We use one comparable 7-day period against another.
    total_loss = abs(
        float(subset["unit_change"].sum())
    )

    if total_loss == 0:
        return 0.0, []

    evidence = []

    # Evaluate the three business dimensions separately.
    dimensions = [
        "region",
        "product_id",
        "channel",
    ]

    dimension_shares = []

    for dimension in dimensions:

        dimension_rows = subset[
            subset["dimension"] == dimension
        ].copy()

        if dimension_rows.empty:
            continue

        worst = dimension_rows.sort_values(
            "unit_change"
        ).iloc[0]

        worst_loss = abs(
            float(worst["unit_change"])
        )

        share = worst_loss / total_loss

        dimension_shares.append(share)

        evidence.append(
            f"largest {dimension} loss: "
            f"{worst[dimension]} "
            f"({int(worst_loss):,} units)"
        )

    if not dimension_shares:
        return 0.0, evidence

    # Average concentration across dimensions.
    concentration = sum(
        dimension_shares
    ) / len(dimension_shares)

    # Cap segment contribution at 0.15.
    segment_score = min(
        concentration,
        0.15,
    )

    return segment_score, evidence


def _apply_event_context(
    hypothesis_name: str,
    event_context: pd.DataFrame,
) -> tuple[float, list[str]]:

    if event_context.empty:
        return 0.0, []

    score = 0.0
    evidence = []

    for _, event in event_context.iterrows():

        category = str(
            event["event_category"]
        ).lower()

        event_name = event["event_name"]

        if (
            hypothesis_name
            == "Inventory constraint"
            and category == "inventory"
        ):
            score += 0.10

            evidence.append(
                f"business event: {event_name}"
            )

        elif (
            hypothesis_name
            == "Marketing efficiency deterioration"
            and category == "marketing"
        ):
            score += 0.10

            evidence.append(
                f"business event: {event_name}"
            )

        elif (
            hypothesis_name
            == "Marketing efficiency deterioration"
            and category == "competitive"
        ):
            score += 0.05

            evidence.append(
                f"competitive event: {event_name}"
            )

    return min(score, 0.15), evidence


def validate_hypotheses() -> pd.DataFrame:

    hypotheses = pd.read_csv(
        HYPOTHESES_PATH
    )

    attribution = pd.read_csv(
        ATTRIBUTION_PATH
    )

    anomalies = pd.read_csv(
        ANOMALIES_PATH
    )

    if EVENT_CONTEXT_PATH.exists():
        event_context = pd.read_csv(
            EVENT_CONTEXT_PATH
        )
    else:
        event_context = pd.DataFrame()

    if DRILLDOWN_PATH.exists():
        drilldown = pd.read_csv(
            DRILLDOWN_PATH
        )
    else:
        drilldown = pd.DataFrame()

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

    if not event_context.empty:
        event_context = event_context[
            event_context["event_date"]
            <= latest_date
        ].copy()

    if not drilldown.empty:
        drilldown = drilldown[
            drilldown["date"] == latest_date
        ].copy()

    results = []

    for _, hypothesis in hypotheses.iterrows():

        name = hypothesis["hypothesis"]

        statistical_score, supporting, contradicting = (
            _score_hypothesis(
                name,
                attribution,
            )
        )

        event_score, event_evidence = (
            _apply_event_context(
                name,
                event_context,
            )
        )

        segment_score = 0.0
        segment_evidence = []

        if name == "Sales volume deterioration":
            segment_score, segment_evidence = (
                _score_segment_evidence(
                    drilldown
                )
            )

        total_score = min(
            statistical_score
            + event_score
            + segment_score,
            1.0,
        )

        supporting.extend(event_evidence)

        if segment_evidence:
            supporting.extend(
                segment_evidence
            )

        if total_score >= 0.75:
            status = "strongly_supported"
        elif total_score >= 0.40:
            status = "supported"
        elif total_score > 0:
            status = "weakly_supported"
        else:
            status = "unsupported"

        results.append(
            {
                "date": latest_date,
                "hypothesis": name,
                "validation_score": round(
                    total_score,
                    2,
                ),
                "statistical_score": round(
                    statistical_score,
                    2,
                ),
                "event_context_score": round(
                    event_score,
                    2,
                ),
                "segment_evidence_score": round(
                    segment_score,
                    2,
                ),
                "status": status,
                "supporting_evidence": "; ".join(
                    supporting
                ),
                "contradicting_evidence": "; ".join(
                    contradicting
                ),
                "anomaly_count": len(anomalies),
                "event_count": len(event_context),
            }
        )

    result = pd.DataFrame(results)

    if not result.empty:

        result = result.sort_values(
            "validation_score",
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

    if result.empty:
        print("No hypotheses available.")
    else:
        print(
            result.to_string(index=False)
        )

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
