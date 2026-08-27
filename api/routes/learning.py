from fastapi import APIRouter

from api.dependencies import read_csv


router = APIRouter(
    prefix="/learning",
    tags=["learning"],
)


@router.get("")
def get_learning():
    df = read_csv("hypothesis_history.csv")

    return {
        "count": len(df),
        "hypotheses": df.to_dict(
            orient="records"
        ),
    }
