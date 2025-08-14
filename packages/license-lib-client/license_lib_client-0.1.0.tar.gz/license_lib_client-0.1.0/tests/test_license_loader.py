import pytest
import json
import base64
import binascii
from unittest.mock import patch, mock_open, MagicMock
from license_lib.utils import LicenseLoader


@pytest.fixture
def valid_license_data():
    return {
        "customer_name": "Test Customer",
        "license_type": "standard",
        "expiration_date": "2099-12-31",
        "features": ["feature1", "feature2"],
        "binding_id": "BIND123",
        "license_id": "LIC123",
        "status": "active",
        "signature": base64.b64encode(b"test_signature").decode()
    }


@pytest.fixture
def license_loader(tmp_path):
    license_file = tmp_path / "license.json"
    return LicenseLoader(str(license_file))


def test_load_license_success(license_loader, valid_license_data):
    """Test successful license loading."""
    with patch("builtins.open", mock_open(read_data=json.dumps(valid_license_data))):
        result = license_loader._load_license()
    
    assert result == valid_license_data
    assert license_loader._license_data == valid_license_data
    assert license_loader._signature == b"test_signature"


def test_load_license_without_signature(license_loader):
    """Test license loading without signature field."""
    license_data = {
        "customer_name": "Test Customer",
        "license_type": "standard",
        "expiration_date": "2099-12-31",
        "features": ["feature1"],
        "binding_id": "BIND123",
        "license_id": "LIC123",
        "status": "active"
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(license_data))):
        result = license_loader._load_license()
    
    assert result == license_data
    assert license_loader._signature is None


def test_load_license_invalid_base64_signature(license_loader):
    """Test license loading with invalid Base64 signature."""
    license_data = {
        "customer_name": "Test Customer",
        "license_type": "standard",
        "expiration_date": "2099-12-31",
        "features": ["feature1"],
        "binding_id": "BIND123",
        "license_id": "LIC123",
        "status": "active",
        "signature": "invalid_base64!"
    }
    
    with patch("builtins.open", mock_open(read_data=json.dumps(license_data))):
        with pytest.raises(ValueError, match="Invalid license format: signature is not valid Base64"):
            license_loader._load_license()


def test_load_license_file_not_found(license_loader):
    """Test license loading when file doesn't exist."""
    with patch("builtins.open", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError):
            license_loader._load_license()


def test_load_license_invalid_json(license_loader):
    """Test license loading with invalid JSON."""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with pytest.raises(json.JSONDecodeError):
            license_loader._load_license()


def test_load_license_cached_data(license_loader, valid_license_data):
    """Test that cached license data is returned."""
    license_loader._license_data = valid_license_data.copy()
    
    result = license_loader._load_license()
    
    assert result == valid_license_data
    # Should not call open() since data is cached
    assert result is not valid_license_data  # Should be a copy


def test_get_signature_with_cached_signature(license_loader):
    """Test getting signature when already cached."""
    license_loader._signature = b"cached_signature"
    result = license_loader._get_signature()
    assert result == b"cached_signature"


def test_get_signature_loads_license(license_loader, valid_license_data):
    """Test getting signature when not cached."""
    with patch("builtins.open", mock_open(read_data=json.dumps(valid_license_data))):
        result = license_loader._get_signature()
    
    assert result == b"test_signature"


def test_get_signature_loads_license_exception(license_loader):
    """Test getting signature when license loading fails."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = license_loader._get_signature()
    
    assert result is None


def test_get_license_data_with_data(license_loader, valid_license_data):
    """Test getting license data when available."""
    license_loader._license_data = valid_license_data.copy()
    result = license_loader._get_license_data()
    
    assert result == valid_license_data
    assert result is not valid_license_data  # Should be a copy


def test_get_license_data_without_data(license_loader):
    """Test getting license data when not available."""
    result = license_loader._get_license_data()
    assert result is None


def test_reload_license(license_loader, valid_license_data):
    """Test force reloading license data."""
    # Set initial cached data
    license_loader._license_data = {"old": "data"}
    license_loader._signature = b"old_signature"
    
    with patch("builtins.open", mock_open(read_data=json.dumps(valid_license_data))):
        result = license_loader._reload_license()
    
    assert result == valid_license_data
    assert license_loader._license_data == valid_license_data
    assert license_loader._signature == b"test_signature"


def test_validate_license_structure_valid(valid_license_data):
    """Test license structure validation with valid data."""
    assert LicenseLoader.validate_license_structure(valid_license_data) is True


def test_validate_license_structure_missing_field(valid_license_data):
    """Test license structure validation with missing field."""
    del valid_license_data["customer_name"]
    assert LicenseLoader.validate_license_structure(valid_license_data) is False


def test_validate_license_structure_invalid_features(valid_license_data):
    """Test license structure validation with invalid features field."""
    valid_license_data["features"] = "not_a_list"
    assert LicenseLoader.validate_license_structure(valid_license_data) is False


def test_validate_license_structure_missing_features(valid_license_data):
    """Test license structure validation with missing features field."""
    del valid_license_data["features"]
    assert LicenseLoader.validate_license_structure(valid_license_data) is False


def test_get_license_info(valid_license_data):
    """Test extracting license information."""
    result = LicenseLoader.get_license_info(valid_license_data)
    
    expected = {
        "customer_name": "Test Customer",
        "license_type": "standard",
        "expiration_date": "2099-12-31",
        "features": ["feature1", "feature2"],
        "tps_limit": None,
        "binding_id": "BIND123",
        "license_id": "LIC123",
        "created_at": None,
        "version": None,
        "status": "active",
        "signature": base64.b64encode(b"test_signature").decode()
    }
    
    assert result == expected


def test_get_license_info_with_optional_fields():
    """Test extracting license information with optional fields."""
    license_data = {
        "customer_name": "Test Customer",
        "license_type": "standard",
        "expiration_date": "2099-12-31",
        "features": ["feature1"],
        "binding_id": "BIND123",
        "license_id": "LIC123",
        "status": "active",
        "signature": "test_sig",
        "tps_limit": 1000,
        "created_at": "2023-01-01",
        "version": "1.0.0"
    }
    
    result = LicenseLoader.get_license_info(license_data)
    
    assert result["tps_limit"] == 1000
    assert result["created_at"] == "2023-01-01"
    assert result["version"] == "1.0.0"


def test_get_license_info_with_missing_optional_fields():
    """Test extracting license information with missing optional fields."""
    license_data = {
        "customer_name": "Test Customer",
        "license_type": "standard",
        "expiration_date": "2099-12-31",
        "features": ["feature1"],
        "binding_id": "BIND123",
        "license_id": "LIC123",
        "status": "active",
        "signature": "test_sig"
    }
    
    result = LicenseLoader.get_license_info(license_data)
    
    assert result["tps_limit"] is None
    assert result["created_at"] is None
    assert result["version"] is None
