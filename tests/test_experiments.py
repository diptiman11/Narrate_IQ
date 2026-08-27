import pandas as pd

from src.experiments.service import (
    complete_experiment,
)


def test_success_classification():
    baseline = 100.0
    observed = 106.0
    threshold = 5.0

    measured_change = (
        (observed - baseline)
        / abs(baseline)
        * 100
    )

    assert measured_change >= threshold


def test_partial_classification():
    baseline = 100.0
    observed = 103.0
    threshold = 5.0

    measured_change = (
        (observed - baseline)
        / abs(baseline)
        * 100
    )

    assert 0 < measured_change < threshold
