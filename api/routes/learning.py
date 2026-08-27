from fastapi import APIRouter, HTTPException

from api.dependencies import read_csv
from api.serializers import clean_records


router = APIRouter(
    prefix="/learning",
    tags=["learning"],
)


@router.get("")
def get_learning():
    try:
        summary = read_csv(
            "hypothesis_history.csv"
        )
    except HTTPException as exc:
        if exc.status_code != 404:
            raise
        summary = None

    try:
        history = read_csv(
            "experiment_history.csv"
        )
    except HTTPException as exc:
        if exc.status_code != 404:
            raise
        history = None

    if (
        (summary is None or summary.empty)
        and (history is None or history.empty)
    ):
        raise HTTPException(
            status_code=404,
            detail="No learning history is available.",
        )

    return {
        "summary": (
            clean_records(
                summary.to_dict(
                    orient="records"
                )
            )
            if summary is not None
            else []
        ),
        "history": (
            clean_records(
                history.to_dict(
                    orient="records"
                )
            )
            if history is not None
            else []
        ),
    }
