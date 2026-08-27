from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class KPIResponse(BaseModel):
    rows: int
    latest: dict[str, Any]


class AnomaliesResponse(BaseModel):
    count: int
    latest: list[dict[str, Any]]


class DriversResponse(BaseModel):
    rows: int
    latest: list[dict[str, Any]]


class AttributionResponse(BaseModel):
    date: str | None
    drivers: list[dict[str, Any]]


class ConfidenceResponse(BaseModel):
    date: str | None
    drivers: list[dict[str, Any]]


class RecommendationsResponse(BaseModel):
    count: int
    recommendations: list[dict[str, Any]]


class NarrativeResponse(BaseModel):
    narrative: str


class InsightResponse(BaseModel):
    date: str
    kpi: dict[str, Any]

    anomalies: list[dict[str, Any]]
    drivers: list[dict[str, Any]]
    attribution: list[dict[str, Any]]
    confidence: list[dict[str, Any]]

    hypotheses: list[dict[str, Any]]
    evidence_validation: list[dict[str, Any]]
    drilldown: list[dict[str, Any]]

    recommendations: list[dict[str, Any]]
    narrative: str | None