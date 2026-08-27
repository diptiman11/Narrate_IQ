from typing import Any

import pandas as pd


def clean_value(value: Any) -> Any:
    """
    Convert Pandas NaN/NaT and NumPy scalar values into
    JSON-safe Python values.
    """

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass

    return value


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: clean_value(value)
        for key, value in record.items()
    }


def clean_records(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        clean_record(record)
        for record in records
    ]
