from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="Narrate IQ",
    description="KPI Intelligence-to-Action Engine",
    version="0.1.0",
)


BASE_DIR = Path("data/processed")


def read_csv(filename: str):
    path = BASE_DIR / filename

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{filename} not found. Run the pipeline first.",
        )

    return pd.read_csv(path)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "narrate-iq",
        "version": "0.1.0",
    }


@app.get("/kpis")
def get_kpis():
    df = read_csv("daily_kpis.csv")

    return {
        "rows": len(df),
        "latest": df.iloc[-1].to_dict(),
    }


@app.get("/anomalies")
def get_anomalies():
    df = read_csv("anomalies.csv")

    return {
        "count": len(df),
        "latest": df.tail(20).to_dict(orient="records"),
    }


@app.get("/drivers")
def get_drivers():
    df = read_csv("revenue_driver_ranking.csv")

    return {
        "rows": len(df),
        "latest": df.tail(10).to_dict(orient="records"),
    }


@app.get("/attribution")
def get_attribution():
    df = read_csv("driver_attribution.csv")

    return {
        "date": df["date"].max(),
        "drivers": df.to_dict(orient="records"),
    }


@app.get("/confidence")
def get_confidence():
    df = read_csv("confidence_scores.csv")

    return {
        "date": df["date"].max(),
        "drivers": df.to_dict(orient="records"),
    }


@app.get("/recommendations")
def get_recommendations():
    df = read_csv("recommendations.csv")

    return {
        "count": len(df),
        "recommendations": df.to_dict(
            orient="records"
        ),
    }


@app.get("/narrative")
def get_narrative():

    path = BASE_DIR / "business_narrative.txt"

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="business_narrative.txt not found. "
                   "Run the narrative pipeline first.",
        )

    return {
        "narrative": path.read_text(
            encoding="utf-8"
        )
    }