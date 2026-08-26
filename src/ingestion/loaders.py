from pathlib import Path

import pandas as pd

from .schemas import ALL_SOURCES, DataSource


class DataValidationError(Exception):
    """Raised when an input dataset fails validation."""


def load_csv(source: DataSource) -> pd.DataFrame:
    path = source.path

    if not path.exists():
        raise FileNotFoundError(
            f"Required data source '{source.name}' was not found at {path}"
        )

    df = pd.read_csv(path)

    missing_columns = set(source.required_columns) - set(df.columns)

    if missing_columns:
        raise DataValidationError(
            f"{source.name}: missing columns: "
            f"{sorted(missing_columns)}"
        )

    if source.date_column:
        df[source.date_column] = pd.to_datetime(
            df[source.date_column],
            format=source.date_format,
            errors="coerce",
        )

        invalid_dates = df[source.date_column].isna().sum()

        if invalid_dates:
            raise DataValidationError(
                f"{source.name}: {invalid_dates} invalid dates "
                f"in '{source.date_column}'"
            )

    return df


def validate_basic_quality(
    df: pd.DataFrame,
    source: DataSource,
) -> dict:
    duplicate_rows = int(df.duplicated().sum())
    missing_values = int(df.isna().sum().sum())

    return {
        "source": source.name,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": duplicate_rows,
        "missing_values": missing_values,
        "date_min": (
            df[source.date_column].min().isoformat()
            if source.date_column
            else None
        ),
        "date_max": (
            df[source.date_column].max().isoformat()
            if source.date_column
            else None
        ),
    }


def load_all_sources() -> dict[str, pd.DataFrame]:
    datasets = {}

    for source in ALL_SOURCES:
        datasets[source.name] = load_csv(source)

    return datasets