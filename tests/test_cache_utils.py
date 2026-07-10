import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.cache_utils import (
    get_gates,
    get_transportation,
    get_accessibility_info,
    get_emergency_info,
)


def test_get_gates_returns_list_of_dicts():
    gates = get_gates()
    assert isinstance(gates, list)
    assert len(gates) > 0
    for gate in gates:
        assert "id" in gate
        assert "crowd_status" in gate


def test_get_gates_crowd_status_values_are_valid():
    valid_statuses = {"Low", "Medium", "High"}
    for gate in get_gates():
        assert gate["crowd_status"] in valid_statuses


def test_get_transportation_has_expected_keys():
    transport = get_transportation()
    expected_keys = {"metro", "bus", "taxi_pickup", "rideshare", "parking"}
    assert expected_keys.issubset(transport.keys())


def test_get_accessibility_info_has_wheelchair_routes():
    info = get_accessibility_info()
    assert "wheelchair_routes" in info
    assert isinstance(info["wheelchair_routes"], list)


def test_get_emergency_info_has_required_fields():
    info = get_emergency_info()
    assert "nearest_medical_center" in info
    assert "emergency_exit" in info
