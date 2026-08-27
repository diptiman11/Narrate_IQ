from fastapi import APIRouter, HTTPException

from api.dependencies import read_csv


router = APIRouter(
    prefix="/drilldown",
    tags=["drilldown"],
)


def _clean_record(record: dict) -> dict:
    """
    Convert pandas NaN values to JSON-safe None values.
    """
    cleaned = {}

    for key, value in record.items():
        if value != value:
            cleaned[key] = None
        else:
            cleaned[key] = value

    return cleaned


@router.get("/sales")
def get_sales_drilldown():
    df = read_csv(
        "sales_dimension_drilldown.csv"
    )

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=(
                "sales_dimension_drilldown.csv "
                "contains no data."
            ),
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
        "results": [
            _clean_record(record)
            for record in records
        ],
    }
