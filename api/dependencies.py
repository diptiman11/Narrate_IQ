from pathlib import Path

import pandas as pd
from fastapi import HTTPException


BASE_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def read_csv(filename: str) -> pd.DataFrame:
    path = BASE_DIR / filename

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{filename} not found. Run the pipeline first.",
        )

    try:
        return pd.read_csv(path)
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
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read business narrative: {exc}",
        ) from exc
