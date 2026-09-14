from datetime import date, timedelta

import pytest


@pytest.fixture
def seven_observations():
    start = date(2024, 1, 1)
    return [
        {
            "date": (start + timedelta(days=index)).isoformat(),
            "temperature": float(10 + index),
            "precipitation": float(index % 2),
            "wind_speed": float(4 + index),
        }
        for index in range(7)
    ]
