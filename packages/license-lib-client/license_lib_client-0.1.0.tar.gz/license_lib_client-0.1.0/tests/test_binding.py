import pytest
from unittest.mock import patch, mock_open
import hashlib
import subprocess
import platform
import builtins
from unittest.mock import MagicMock

from license_lib.binding_id import (
    _get_mac_address,
    _get_cpu_info,
    _get_system_uuid,
    generate_binding_id,
    verify_binding_id,
)

# ---------- MAC ADDRESS TESTS ----------

def test_get_mac_address_valid(monkeypatch):
    import uuid
    monkeypatch.setattr(uuid, "getnode", lambda: 0x001122334455)
    assert _get_mac_address() == "00:11:22:33:44:55"

def test_get_mac_address_local_admin(monkeypatch):
    import uuid
    mac_val = (0x02 << 40) | 0x001122334455  # locally administered bit
    monkeypatch.setattr(uuid, "getnode", lambda: mac_val)
    assert _get_mac_address() is None

def test_get_mac_address_exception(monkeypatch):
    import uuid
    monkeypatch.setattr(uuid, "getnode", lambda: "invalid")
    assert _get_mac_address() is None

# ---------- CPU INFO TESTS ----------

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_cpu_info_windows(mock_check):
    mock_check.return_value = b"Intel(R) Core(TM) i7-9700 CPU"
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        assert "Intel" in _get_cpu_info()

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_cpu_info_windows_empty_result(mock_check):
    mock_check.return_value = b""
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        assert _get_cpu_info() == "UNKNOWN"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_cpu_info_windows_exception(mock_check):
    mock_check.side_effect = subprocess.CalledProcessError(1, "cmd")
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        assert _get_cpu_info() == "UNKNOWN"

def test_get_cpu_info_linux_success():
    mock_file = mock_open(read_data="processor : 0\nmodel name : AMD Ryzen 5 3600\n")
    with patch("license_lib.binding_id.platform.system", return_value="Linux"):
        with patch("builtins.open", mock_file):
            assert "AMD Ryzen" in _get_cpu_info()

def test_get_cpu_info_linux_file_not_found():
    with patch("license_lib.binding_id.platform.system", return_value="Linux"):
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert _get_cpu_info() == "UNKNOWN"

def test_get_cpu_info_linux_no_model_name():
    mock_file = mock_open(read_data="processor : 0\nvendor_id : GenuineIntel\n")
    with patch("license_lib.binding_id.platform.system", return_value="Linux"):
        with patch("builtins.open", mock_file):
            assert _get_cpu_info() == "UNKNOWN"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_cpu_info_darwin(mock_check):
    mock_check.return_value = b"Apple M1"
    with patch("license_lib.binding_id.platform.system", return_value="Darwin"):
        assert "Apple" in _get_cpu_info()

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_cpu_info_darwin_empty_result(mock_check):
    mock_check.return_value = b""
    with patch("license_lib.binding_id.platform.system", return_value="Darwin"):
        assert _get_cpu_info() == "UNKNOWN"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_cpu_info_darwin_exception(mock_check):
    mock_check.side_effect = subprocess.CalledProcessError(1, "cmd")
    with patch("license_lib.binding_id.platform.system", return_value="Darwin"):
        assert _get_cpu_info() == "UNKNOWN"

def test_get_cpu_info_unknown_system():
    with patch("license_lib.binding_id.platform.system", return_value="UnknownOS"):
        assert _get_cpu_info() == "UNKNOWN"

def test_get_cpu_info_exception():
    with patch("license_lib.binding_id.platform.system", side_effect=Exception("test")):
        assert _get_cpu_info() == "UNKNOWN"

# ---------- SYSTEM UUID TESTS ----------

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_system_uuid_windows(mock_check):
    mock_check.return_value = b"1234-UUID-5678"
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        assert _get_system_uuid() == "1234-UUID-5678"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_system_uuid_windows_empty_result(mock_check):
    mock_check.return_value = b""
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        assert _get_system_uuid() == "UNKNOWN"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_system_uuid_windows_exception(mock_check):
    mock_check.side_effect = subprocess.CalledProcessError(1, "cmd")
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_linux_machine_id():
    mock_file = mock_open(read_data="machine-uuid-1234")
    with patch("license_lib.binding_id.platform.system", return_value="Linux"):
        with patch("builtins.open", mock_file):
            assert _get_system_uuid() == "machine-uuid-1234"

def test_get_system_uuid_linux_machine_id_not_found_product_uuid():
    # First call raises FileNotFoundError, second call succeeds
    mock_file = mock_open(read_data="product-uuid-5678")
    
    def side_effect(path, *args, **kwargs):
        if "machine-id" in str(path):
            raise FileNotFoundError()
        return mock_file(path, *args, **kwargs)
    
    with patch("license_lib.binding_id.platform.system", return_value="Linux"):
        with patch("builtins.open", side_effect=side_effect):
            assert _get_system_uuid() == "product-uuid-5678"

def test_get_system_uuid_linux_both_files_not_found():
    with patch("license_lib.binding_id.platform.system", return_value="Linux"):
        with patch("builtins.open", side_effect=FileNotFoundError):
            assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_linux_product_uuid_exception():
    def side_effect(path, *args, **kwargs):
        if "machine-id" in str(path):
            raise FileNotFoundError()
        elif "product_uuid" in str(path):
            raise Exception("test")
        raise FileNotFoundError()
    
    with patch("license_lib.binding_id.platform.system", return_value="Linux"):
        with patch("builtins.open", side_effect=side_effect):
            assert _get_system_uuid() == "UNKNOWN"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_system_uuid_darwin_success(mock_check):
    mock_check.return_value = b'IOPlatformUUID = "darwin-uuid-1234"'
    with patch("license_lib.binding_id.platform.system", return_value="Darwin"):
        assert _get_system_uuid() == "darwin-uuid-1234"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_system_uuid_darwin_no_uuid_line(mock_check):
    mock_check.return_value = b"Some other output without IOPlatformUUID"
    with patch("license_lib.binding_id.platform.system", return_value="Darwin"):
        assert _get_system_uuid() == "UNKNOWN"

@patch("license_lib.binding_id.subprocess.check_output")
def test_get_system_uuid_darwin_exception(mock_check):
    mock_check.side_effect = subprocess.CalledProcessError(1, "cmd")
    with patch("license_lib.binding_id.platform.system", return_value="Darwin"):
        assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_unknown_system():
    with patch("license_lib.binding_id.platform.system", return_value="UnknownOS"):
        assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_exception():
    with patch("license_lib.binding_id.platform.system", side_effect=Exception("test")):
        assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_windows_exception():
    """Test Windows UUID retrieval with subprocess exception."""
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        with patch("license_lib.binding_id.subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "cmd")):
            assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_windows_decode_exception():
    """Test Windows UUID retrieval with decode exception."""
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        with patch("license_lib.binding_id.subprocess.check_output", side_effect=UnicodeDecodeError("utf-8", b"test", 0, 1, "test")):
            assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_windows_general_exception():
    """Test Windows UUID retrieval with general exception."""
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        with patch("license_lib.binding_id.subprocess.check_output", side_effect=OSError("test")):
            assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_platform_exception():
    """Test _get_system_uuid with platform.system exception."""
    with patch("license_lib.binding_id.platform.system", side_effect=Exception("platform error")):
        assert _get_system_uuid() == "UNKNOWN"

def test_get_system_uuid_windows_decode_strip_exception():
    """Test Windows UUID retrieval with decode.strip exception."""
    mock_result = MagicMock()
    mock_result.decode.return_value.strip.side_effect = Exception("strip error")
    
    with patch("license_lib.binding_id.platform.system", return_value="Windows"):
        with patch("license_lib.binding_id.subprocess.check_output", return_value=mock_result):
            assert _get_system_uuid() == "UNKNOWN"

# ---------- BINDING ID TESTS ----------

def test_generate_binding_id_consistency(monkeypatch):
    monkeypatch.setattr("license_lib.binding_id._get_mac_address", lambda: "00:11:22:33:44:55")
    monkeypatch.setattr("license_lib.binding_id._get_cpu_info", lambda: "INTEL CPU")
    monkeypatch.setattr("license_lib.binding_id._get_system_uuid", lambda: "SYSTEM-UUID")

    id1 = generate_binding_id()
    id2 = generate_binding_id()
    assert id1 == id2
    assert isinstance(id1, str)
    assert len(id1) == 64

def test_generate_binding_id_with_none_values(monkeypatch):
    monkeypatch.setattr("license_lib.binding_id._get_mac_address", lambda: None)
    monkeypatch.setattr("license_lib.binding_id._get_cpu_info", lambda: None)
    monkeypatch.setattr("license_lib.binding_id._get_system_uuid", lambda: None)

    binding_id = generate_binding_id()
    expected = hashlib.sha256("UNKNOWN-UNKNOWN-UNKNOWN".encode()).hexdigest()
    assert binding_id == expected

def test_generate_binding_id_with_empty_values(monkeypatch):
    monkeypatch.setattr("license_lib.binding_id._get_mac_address", lambda: "")
    monkeypatch.setattr("license_lib.binding_id._get_cpu_info", lambda: "")
    monkeypatch.setattr("license_lib.binding_id._get_system_uuid", lambda: "")

    binding_id = generate_binding_id()
    expected = hashlib.sha256("UNKNOWN-UNKNOWN-UNKNOWN".encode()).hexdigest()
    assert binding_id == expected

def test_verify_binding_id_match(monkeypatch):
    monkeypatch.setattr("license_lib.binding_id.generate_binding_id", lambda: "ABC123")
    assert verify_binding_id("abc123") is True

def test_verify_binding_id_mismatch(monkeypatch):
    monkeypatch.setattr("license_lib.binding_id.generate_binding_id", lambda: "ABC123")
    assert verify_binding_id("XYZ789") is False

def test_verify_binding_id_with_whitespace(monkeypatch):
    monkeypatch.setattr("license_lib.binding_id.generate_binding_id", lambda: "  ABC123  ")
    assert verify_binding_id("  abc123  ") is True

def test_verify_binding_id_case_insensitive(monkeypatch):
    monkeypatch.setattr("license_lib.binding_id.generate_binding_id", lambda: "ABC123")
    assert verify_binding_id("abc123") is True
    assert verify_binding_id("ABC123") is True
    assert verify_binding_id("AbC123") is True
