from fastapi import APIRouter, HTTPException

from api.dependencies import read_csv, read_narrative
from api.schemas import (
    AnomaliesResponse,
    AttributionResponse,
    ConfidenceResponse,
    DriversResponse,
    InsightResponse,
    KPIResponse,
    NarrativeResponse,
    RecommendationsResponse,
)


router = APIRouter()


@router.get("/kpis", response_model=KPIResponse)
def get_kpis():
    df = read_csv("daily_kpis.csv")

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="daily_kpis.csv contains no data.",
        )

    return {
        "rows": len(df),
        "latest": df.iloc[-1].to_dict(),
    }


@router.get("/anomalies", response_model=AnomaliesResponse)
def get_anomalies():
    df = read_csv("anomalies.csv")

    return {
        "count": len(df),
        "latest": df.tail(20).to_dict(
            orient="records"
        ),
    }


@router.get("/drivers", response_model=DriversResponse)
def get_drivers():
    df = read_csv("revenue_driver_ranking.csv")

    return {
        "rows": len(df),
        "latest": df.tail(10).to_dict(
            orient="records"
        ),
    }


@router.get("/attribution", response_model=AttributionResponse)
def get_attribution():
    df = read_csv("driver_attribution.csv")

    if df.empty:
        return {
            "date": None,
            "drivers": [],
        }

    latest_date = df["date"].max()

    return {
        "date": latest_date,
        "drivers": df[
            df["date"] == latest_date
        ].to_dict(orient="records"),
    }


@router.get("/confidence", response_model=ConfidenceResponse)
def get_confidence():
    df = read_csv("confidence_scores.csv")

    if df.empty:
        return {
            "date": None,
            "drivers": [],
        }

    latest_date = df["date"].max()

    return {
        "date": latest_date,
        "drivers": df[
            df["date"] == latest_date
        ].to_dict(orient="records"),
    }


@router.get(
    "/recommendations",
    response_model=RecommendationsResponse,
)
def get_recommendations():
    df = read_csv("recommendations.csv")

    return {
        "count": len(df),
        "recommendations": df.to_dict(
            orient="records"
        ),
    }


@router.get(
    "/narrative",
    response_model=NarrativeResponse,
)
def get_narrative():
    narrative = read_narrative()

    if narrative is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "business_narrative.txt not found. "
                "Run the narrative pipeline first."
            ),
        )

    return {
        "narrative": narrative,
    }


@router.get(
    "/analysis",
    response_model=InsightResponse,
)
def get_analysis():
    """
    Complete Narrate IQ intelligence-to-action analysis.
    """

    kpis = read_csv("daily_kpis.csv")
    anomalies = read_csv("anomalies.csv")
    drivers = read_csv("revenue_driver_ranking.csv")
    attribution = read_csv("driver_attribution.csv")
    confidence = read_csv("confidence_scores.csv")
    hypotheses = read_csv("hypotheses.csv")
    evidence_validation = read_csv(
        "evidence_validation.csv"
    )
    drilldown = read_csv(
        "sales_dimension_drilldown.csv"
    )
    recommendations = read_csv("recommendations.csv")

    if kpis.empty:
        raise HTTPException(
            status_code=404,
            detail="daily_kpis.csv contains no data.",
        )

    if drilldown.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "sales_dimension_drilldown.csv "
                "contains no data."
            ),
        )

    latest_date = kpis["date"].max()

    return {
        "date": latest_date,

        "kpi": kpis.iloc[-1].to_dict(),

        "anomalies": anomalies.tail(20).to_dict(
            orient="records"
        ),

        "drivers": drivers.tail(10).to_dict(
            orient="records"
        ),

        "attribution": attribution[
            attribution["date"] == latest_date
        ].to_dict(orient="records"),

        "confidence": confidence[
            confidence["date"] == latest_date
        ].to_dict(orient="records"),

        "hypotheses": hypotheses[
            hypotheses["date"] == latest_date
        ].to_dict(orient="records"),

        "evidence_validation": evidence_validation[
            evidence_validation["date"] == latest_date
        ].to_dict(orient="records"),

        "drilldown": drilldown[
            drilldown["date"] == latest_date
        ].to_dict(orient="records"),

        "recommendations": recommendations[
            recommendations["date"] == latest_date
        ].to_dict(orient="records"),

        "narrative": read_narrative(),
    }