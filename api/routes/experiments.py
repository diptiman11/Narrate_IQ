from fastapi import APIRouter, HTTPException

from api.dependencies import read_csv
from api.experiment_schemas import (
    ExperimentOutcomeRequest,
    ExperimentResponse,
    ExperimentStartRequest,
)
from src.experiments.service import (
    complete_experiment,
    start_experiment,
)


router = APIRouter(
    prefix="/experiments",
    tags=["experiments"],
)


def _clean_record(record: dict) -> dict:
    """
    Convert pandas NaN values into Python None so that
    Pydantic can correctly validate optional fields.
    """
    cleaned = {}

    for key, value in record.items():
        if value != value:
            cleaned[key] = None
        else:
            cleaned[key] = value

    return cleaned


@router.get(
    "",
    response_model=list[ExperimentResponse],
)
def get_experiments():
    df = read_csv("experiments.csv")

    records = df.to_dict(orient="records")

    return [
        _clean_record(record)
        for record in records
    ]


@router.post(
    "/{experiment_id}/start",
    response_model=ExperimentResponse,
)
def start_experiment_endpoint(
    experiment_id: str,
    request: ExperimentStartRequest,
):
    try:
        result = start_experiment(
            experiment_id=experiment_id,
            baseline_value=request.baseline_value,
        )

        return _clean_record(result)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post(
    "/{experiment_id}/outcome",
    response_model=ExperimentResponse,
)
def complete_experiment_endpoint(
    experiment_id: str,
    request: ExperimentOutcomeRequest,
):
    try:
        result = complete_experiment(
            experiment_id=experiment_id,
            observed_value=request.observed_value,
        )

        return _clean_record(result)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
