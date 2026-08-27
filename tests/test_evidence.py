import pandas as pd

from src.evidence.validator import _score_hypothesis


def test_sales_volume_hypothesis_scores_strongly():
    attribution = pd.DataFrame(
        [
            {
                "driver": "sales_units",
                "driver_change_pct": -7.8,
                "model_importance_pct": 99.17,
            }
        ]
    )

    score, supporting, contradicting = _score_hypothesis(
        "Sales volume deterioration",
        attribution,
    )

    assert score == 0.8
    assert len(supporting) == 2
    assert contradicting == []


def test_inventory_hypothesis_scores_from_two_signals():
    attribution = pd.DataFrame(
        [
            {
                "driver": "stockout_hours",
                "driver_change_pct": 15.79,
                "model_importance_pct": 0.7,
            },
            {
                "driver": "closing_stock",
                "driver_change_pct": -5.23,
                "model_importance_pct": 0.0,
            },
        ]
    )

    score, supporting, contradicting = _score_hypothesis(
        "Inventory constraint",
        attribution,
    )

    assert score == 0.5
    assert len(supporting) == 2
    assert contradicting == []
