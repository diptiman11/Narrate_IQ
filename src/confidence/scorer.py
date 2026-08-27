from pathlib import Path

import pandas as pd


KPI_PATH = "data/processed/daily_kpis.csv"
ATTRIBUTION_PATH = "data/processed/driver_attribution.csv"
ANOMALY_PATH = "data/processed/anomalies.csv"

OUTPUT_PATH = "data/processed/confidence_scores.csv"


def calculate_confidence() -> pd.DataFrame:

    kpis = pd.read_csv(KPI_PATH)
    attribution = pd.read_csv(ATTRIBUTION_PATH)
    anomalies = pd.read_csv(ANOMALY_PATH)

    latest_date = kpis["date"].max()

    latest_kpi = kpis[
        kpis["date"] == latest_date
    ].iloc[0]

    latest_attr = attribution[
        attribution["date"] == latest_date
    ].copy()

    latest_anomalies = anomalies[
        anomalies["date"] == latest_date
    ]

    rows = []

    for _, driver in latest_attr.iterrows():

        name = driver["driver"]
        importance = driver["model_importance_pct"]

        score = 0.0
        evidence = []

        # ML evidence
        if importance >= 50:
            score += 0.50
            evidence.append("strong_ml")

        elif importance >= 20:
            score += 0.35
            evidence.append("moderate_ml")

        elif importance >= 5:
            score += 0.20
            evidence.append("weak_ml")

        # Anomaly evidence
        anomaly_match = latest_anomalies[
            latest_anomalies["kpi"]
            .astype(str)
            .str.contains(
                name,
                case=False,
                na=False,
            )
        ]

        if len(anomaly_match) > 0:
            score += 0.20
            evidence.append("anomaly")

        # Materiality evidence
        materiality_column = f"{name}_materiality"

        if materiality_column in latest_kpi.index:

            materiality = str(
                latest_kpi[materiality_column]
            ).lower()

            if materiality == "high":
                score += 0.20
                evidence.append("high_materiality")

            elif materiality == "medium":
                score += 0.10
                evidence.append("medium_materiality")

        # Movement evidence
        change = abs(
            float(driver["driver_change_pct"])
        )

        if change >= 5:
            score += 0.10
            evidence.append("meaningful_change")

        elif change >= 2:
            score += 0.05
            evidence.append("moderate_change")

        score = min(score, 1.0)

        if score >= 0.75:
            confidence = "high"

        elif score >= 0.50:
            confidence = "medium"

        else:
            confidence = "low"

        rows.append(
            {
                "date": latest_date,
                "driver": name,
                "driver_change_pct": driver[
                    "driver_change_pct"
                ],
                "ml_importance_pct": importance,
                "confidence_score": round(score, 3),
                "confidence": confidence,
                "evidence": ",".join(evidence),
            }
        )

    result = pd.DataFrame(rows)

    output = Path(OUTPUT_PATH)
    output.parent.mkdir(parents=True, exist_ok=True)

    result.to_csv(
        output,
        index=False,
    )

    return result


def main():

    result = calculate_confidence()

    print(
        "\n=== Narrate IQ Confidence Scoring ===\n"
    )

    print(
        result.to_string(index=False)
    )

    print(
        "\nSaved to: "
        "data/processed/confidence_scores.csv"
    )


if __name__ == "__main__":
    main()