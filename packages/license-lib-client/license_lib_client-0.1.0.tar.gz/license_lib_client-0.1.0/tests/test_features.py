import pytest
from unittest.mock import MagicMock
from license_lib.features import FeatureManager  # Adjust import path


@pytest.fixture
def mock_validator():
    return MagicMock()


@pytest.fixture
def feature_manager(mock_validator):
    return FeatureManager(mock_validator)


def test_get_features_caches_and_updates(feature_manager, mock_validator):
    license_data1 = {"features": ["feat1", "feat2"]}
    license_data2 = {"features": ["feat3"]}

    # First call returns license_data1
    mock_validator._get_raw_license_data.return_value = license_data1
    features = feature_manager._get_features()
    assert features == ["feat1", "feat2"]

    # Change license data to license_data2, cache should update
    mock_validator._get_raw_license_data.return_value = license_data2
    features = feature_manager._get_features()
    assert features == ["feat3"]

    # Calling again with same license data returns cached
    mock_validator._get_raw_license_data.return_value = license_data2
    features = feature_manager._get_features()
    assert features == ["feat3"]


def test_is_feature_enabled_true_and_false(feature_manager, mock_validator):
    mock_validator._get_raw_license_data.return_value = {"features": ["alpha", "beta"]}
    assert feature_manager.is_feature_enabled("alpha")
    assert not feature_manager.is_feature_enabled("gamma")


def test_is_feature_enabled_handles_exception(feature_manager, mock_validator):
    mock_validator._get_raw_license_data.side_effect = Exception("fail")
    assert not feature_manager.is_feature_enabled("any_feature")


def test_get_enabled_features_returns_list(feature_manager, mock_validator):
    mock_validator._get_raw_license_data.return_value = {"features": ["f1", "f2"]}
    features = feature_manager.get_enabled_features()
    assert features == ["f1", "f2"]


def test_get_enabled_features_handles_exception(feature_manager, mock_validator):
    mock_validator._get_raw_license_data.side_effect = Exception("fail")
    features = feature_manager.get_enabled_features()
    assert features == []


def test_check_multiple_features_returns_dict(feature_manager, mock_validator):
    mock_validator._get_raw_license_data.return_value = {"features": ["featA", "featB"]}
    result = feature_manager.check_multiple_features(["featA", "featC"])
    assert result == {"featA": True, "featC": False}


def test_check_multiple_features_handles_exception(feature_manager, mock_validator):
    mock_validator._get_raw_license_data.side_effect = Exception("fail")
    result = feature_manager.check_multiple_features(["featX"])
    assert result == {}
