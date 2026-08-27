import json

from fastapi import APIRouter, HTTPException

from api.dependencies import read_narrative


router = APIRouter(
    prefix="/decision",
    tags=["decision"],
)


@router.get("")
def get_decision():
    path = (
        "data/processed/decision_object.json"
    )

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                "decision_object.json not found. "
                "Run the decision pipeline first."
            ),
        ) from exc
