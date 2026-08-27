import pandas as pd

from api.serializers import clean_record, clean_records


def test_clean_record_converts_nan_to_none():
    record = {
        "value": float("nan"),
        "name": "test",
        "number": 10,
    }

    cleaned = clean_record(record)

    assert cleaned["value"] is None
    assert cleaned["name"] == "test"
    assert cleaned["number"] == 10


def test_clean_records_handles_multiple_rows():
    records = [
        {"value": float("nan")},
        {"value": 5},
    ]

    cleaned = clean_records(records)

    assert cleaned == [
        {"value": None},
        {"value": 5},
    ]


def test_pandas_na_is_cleaned():
    record = {
        "value": pd.NA,
    }

    cleaned = clean_record(record)

    assert cleaned["value"] is None
