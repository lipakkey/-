import pytest

from core.config.models import DeviceAssignment


def test_device_assignment_uniform():
    assignment = DeviceAssignment(device_ids=("d1", "d2", "d3"))
    weights = assignment.normalized_weights()
    assert pytest.approx(weights["d1"]) == 1 / 3
    assert pytest.approx(weights["d2"]) == 1 / 3
    assert pytest.approx(weights["d3"]) == 1 / 3


def test_device_assignment_custom_weights():
    assignment = DeviceAssignment(device_ids=("d1", "d2"), weights={"d1": 2, "d2": 1})
    weights = assignment.normalized_weights()
    assert pytest.approx(weights["d1"]) == 2 / 3
    assert pytest.approx(weights["d2"]) == 1 / 3


def test_device_assignment_invalid_total():
    assignment = DeviceAssignment(device_ids=("d1",), weights={"d1": 0})
    with pytest.raises(ValueError):
        assignment.normalized_weights()
