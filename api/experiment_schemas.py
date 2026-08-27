from typing import Literal

from pydantic import BaseModel, Field


ExperimentStatus = Literal[
    "proposed",
    "running",
    "completed",
]


class ExperimentStartRequest(BaseModel):
    baseline_value: float = Field(
        ...,
        description="KPI value at experiment start.",
    )


class ExperimentOutcomeRequest(BaseModel):
    observed_value: float = Field(
        ...,
        description="KPI value observed after intervention.",
    )


class ExperimentResponse(BaseModel):
    experiment_id: str
    date: str
    hypothesis: str
    hypothesis_rank: int | None
    confidence_score: float
    confidence: str
    status: ExperimentStatus

    action: str
    target_metric: str
    expected_direction: str
    success_threshold_pct: float

    baseline_value: float | None
    observed_value: float | None
    measured_change_pct: float | None
    outcome: str | None