from pathlib import Path

import pandas as pd
from fastapi import HTTPException

from src.repositories.csv_repository import CSVRepository


BASE_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
)


repository = CSVRepository(BASE_DIR)


def read_csv(filename: str) -> pd.DataFrame:
    try:
        return repository.read(filename)

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                f"{filename} not found. "
                "Run the pipeline first."
            ),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read {filename}: {exc}",
        ) from exc


def read_narrative() -> str | None:
    path = BASE_DIR / "business_narrative.txt"

    if not path.exists():
        return None

    try:
        return path.read_text(
            encoding="utf-8"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to read business narrative: "
                f"{exc}"
            ),
        ) from exc
