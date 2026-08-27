from fastapi import APIRouter, HTTPException

from api.dependencies import read_csv


router = APIRouter(
    prefix="/root-cause",
    tags=["root-cause"],
)


def _clean_record(record: dict) -> dict:
    """
    Convert pandas NaN/NaT values into JSON-safe None.
    """
    cleaned = {}

    for key, value in record.items():
        if value != value:
            cleaned[key] = None
        else:
            cleaned[key] = value

    return cleaned


@router.get("")
def get_root_cause():
    df = read_csv("root_cause_graph.csv")

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail="root_cause_graph.csv contains no data.",
        )

    latest_date = df["date"].max()

    latest = df[
        df["date"] == latest_date
    ].copy()

    records = latest.to_dict(
        orient="records"
    )

    return {
        "date": latest_date,
        "count": len(records),
        "graph": [
            _clean_record(record)
            for record in records
        ],
    }
