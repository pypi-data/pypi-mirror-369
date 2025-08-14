import pytest
import json
from unittest.mock import MagicMock, patch, mock_open
from types import SimpleNamespace
from datetime import datetime
import license_lib.validator as lvm
from cryptography.exceptions import InvalidSignature


@pytest.fixture
def valid_license():
    return {
        "customer_name": "Test Customer",
        "license_type": "standard",
        "expiration_date": "2099-12-31",
        "features": ["feature1", "feature2"],
        "binding_id": "BIND123",
        "license_id": "LIC123",
        "status": "active",
        "signature": "test_signature"
    }


@pytest.fixture
def validator():
    return lvm.LicenseValidator("fake_license.json", "fake_key.pem")


def test_validator_init_empty_license_path():
    with pytest.raises(ValueError, match="license_path cannot be empty"):
        lvm.LicenseValidator("", "fake_key.pem")


def test_validator_init_empty_public_key_path():
    with pytest.raises(ValueError, match="public_key_path cannot be empty"):
        lvm.LicenseValidator("fake_license.json", "")


# --------------------------
# LicenseFileHandler tests
# --------------------------

def test_is_license_file_true_false(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))
    assert handler._is_license_file(str(file_path))
    assert not handler._is_license_file(str(tmp_path / "other.json"))


def test_on_modified_triggers_and_cooldown(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))

    validator._on_license_file_changed = MagicMock()
    e = SimpleNamespace(is_directory=False, src_path=str(file_path))
    handler.on_modified(e)
    validator._on_license_file_changed.assert_called_once()

    handler._last_validation_time = 0
    handler._cooldown_seconds = 100
    handler.on_modified(e)  # cooldown prevents re-call


def test_on_modified_ignores_directory(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))
    validator._on_license_file_changed = MagicMock()
    
    e = SimpleNamespace(is_directory=True, src_path=str(file_path))
    handler.on_modified(e)
    validator._on_license_file_changed.assert_not_called()


def test_on_modified_ignores_wrong_file(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))
    validator._on_license_file_changed = MagicMock()
    
    e = SimpleNamespace(is_directory=False, src_path=str(tmp_path / "other.json"))
    handler.on_modified(e)
    validator._on_license_file_changed.assert_not_called()


def test_on_created_on_moved_on_deleted(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))
    validator._on_license_file_changed = MagicMock()

    for method, attr in [
        (handler.on_created, "src_path"),
        (handler.on_moved, "dest_path"),
        (handler.on_deleted, "src_path")
    ]:
        e = SimpleNamespace(is_directory=False, **{attr: str(file_path)})
        method(e)
        validator._on_license_file_changed.assert_called()


def test_on_created_ignores_directory(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))
    validator._on_license_file_changed = MagicMock()
    
    e = SimpleNamespace(is_directory=True, src_path=str(file_path))
    handler.on_created(e)
    validator._on_license_file_changed.assert_not_called()


def test_on_moved_ignores_directory(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))
    validator._on_license_file_changed = MagicMock()
    
    e = SimpleNamespace(is_directory=True, dest_path=str(file_path))
    handler.on_moved(e)
    validator._on_license_file_changed.assert_not_called()


def test_on_deleted_ignores_directory(tmp_path, validator):
    file_path = tmp_path / "license.json"
    handler = lvm.LicenseFileHandler(validator, str(file_path))
    validator._on_license_file_changed = MagicMock()
    
    e = SimpleNamespace(is_directory=True, src_path=str(file_path))
    handler.on_deleted(e)
    validator._on_license_file_changed.assert_not_called()


def test_handle_change_success_and_json_error(validator):
    handler = lvm.LicenseFileHandler(validator, "test.json")
    validator._on_license_file_changed = MagicMock()

    # Success first try
    handler._handle_change()

    # JSON decode then success
    calls = {"count": 0}
    def fake_call():
        calls["count"] += 1
        if calls["count"] == 1:
            raise json.JSONDecodeError("bad", "doc", 0)
    validator._on_license_file_changed.side_effect = fake_call
    handler._handle_change()

    # Unexpected error stops loop
    validator._on_license_file_changed.side_effect = RuntimeError("fail")
    handler._handle_change()


def test_handle_change_max_retries(validator):
    """Test that _handle_change stops after max retries."""
    handler = lvm.LicenseFileHandler(validator, "test.json")
    validator._on_license_file_changed = MagicMock(side_effect=json.JSONDecodeError("test", "test", 0))
    
    with patch('time.sleep'):  # Speed up test
        handler._handle_change()
    
    # Should have tried 5 times and given up
    assert validator._on_license_file_changed.call_count == 5

def test_handle_change_unexpected_exception(validator):
    """Test that _handle_change handles unexpected exceptions."""
    handler = lvm.LicenseFileHandler(validator, "test.json")
    validator._on_license_file_changed = MagicMock(side_effect=ValueError("test"))
    
    handler._handle_change()
    
    # Should have tried once and stopped on unexpected error
    assert validator._on_license_file_changed.call_count == 1

def test_on_license_file_changed_exception(validator):
    """Test exception handling in _on_license_file_changed."""
    with patch.object(validator, 'validate_license', side_effect=Exception("test")):
        validator._on_license_file_changed()
    
    # Should handle exception gracefully

def test_load_public_key_exception(validator):
    """Test exception handling in _load_public_key."""
    with patch('builtins.open', side_effect=Exception("test")):
        result = validator._load_public_key()
        assert result is None

def test_verify_signature_invalid_signature(validator):
    """Test signature verification with invalid signature."""
    # Mock license data with signature
    validator._license_data = {"test": "data", "signature": b"invalid"}
    
    with patch.object(validator.license_loader, '_get_signature', return_value=b"invalid"):
        with patch.object(validator, '_load_public_key', return_value=MagicMock()):
            with patch.object(validator._load_public_key(), 'verify', side_effect=InvalidSignature):
                is_valid, reason = validator._verify_signature()
                assert not is_valid
                assert "signature verification failed" in reason.lower()

def test_verify_signature_value_error(validator):
    """Test signature verification with ValueError."""
    # Mock license data with signature
    validator._license_data = {"test": "data", "signature": b"invalid"}
    
    with patch.object(validator.license_loader, '_get_signature', return_value=b"invalid"):
        with patch.object(validator, '_load_public_key', return_value=MagicMock()):
            with patch.object(validator._load_public_key(), 'verify', side_effect=ValueError("test")):
                is_valid, reason = validator._verify_signature()
                assert not is_valid
                assert "signature verification failed" in reason.lower()

def test_verify_signature_unexpected_exception(validator):
    """Test signature verification with unexpected exception."""
    # Mock license data with signature
    validator._license_data = {"test": "data", "signature": b"invalid"}
    
    with patch.object(validator.license_loader, '_get_signature', return_value=b"invalid"):
        with patch.object(validator, '_load_public_key', return_value=MagicMock()):
            with patch.object(validator._load_public_key(), 'verify', side_effect=Exception("test")):
                is_valid, reason = validator._verify_signature()
                assert not is_valid
                assert "unexpected error" in reason.lower()

def test_check_expiration_invalid_format(validator):
    """Test expiration check with invalid date format."""
    validator._license_data = {"expiration_date": "invalid-date"}
    
    is_valid, reason = validator._check_expiration()
    assert not is_valid
    assert "invalid expiration date format" in reason.lower()

def test_check_expiration_exception(validator):
    """Test expiration check with unexpected exception."""
    validator._license_data = {"expiration_date": "2023-12-31"}
    
    with patch('license_lib.validator.datetime') as mock_datetime:
        mock_datetime.strptime.side_effect = Exception("test")
        is_valid, reason = validator._check_expiration()
        assert not is_valid
        assert "unexpected error" in reason.lower()

def test_verify_binding_exception(validator):
    """Test binding verification with unexpected exception."""
    validator._license_data = {"binding_id": "test-binding"}
    
    with patch('license_lib.validator.generate_binding_id', side_effect=Exception("test")):
        is_valid, reason = validator._verify_binding()
        assert not is_valid
        assert "unexpected error" in reason.lower()

def test_get_raw_license_data_load_exception(validator):
    """Test _get_raw_license_data when loading fails."""
    with patch.object(validator.license_loader, '_load_license', side_effect=Exception("test")):
        result = validator._get_raw_license_data()
        assert result is None

def test_get_raw_license_data_no_data(validator):
    """Test _get_raw_license_data when no data is available."""
    with patch.object(validator.license_loader, '_load_license', return_value=None):
        result = validator._get_raw_license_data()
        assert result is None

def test_values_different_lists_json_error(validator):
    """Test _values_different with lists that cause JSON serialization error."""
    old_value = [{"key": "value"}]
    new_value = [{"key": "value"}]
    
    with patch('json.dumps', side_effect=TypeError("test")):
        result = validator._values_different(old_value, new_value)
        assert result is False  # Should fall back to direct comparison

def test_values_different_dicts_different_values(validator):
    """Test _values_different with dictionaries that have different values."""
    old_value = {"key": "old_value"}
    new_value = {"key": "new_value"}
    
    result = validator._values_different(old_value, new_value)
    assert result is True

def test_values_different_dicts_different_keys(validator):
    """Test _values_different with dictionaries that have different keys."""
    old_value = {"key1": "value"}
    new_value = {"key2": "value"}
    
    result = validator._values_different(old_value, new_value)
    assert result is True

def test_values_different_dicts_same(validator):
    """Test _values_different with identical dictionaries."""
    old_value = {"key": "value"}
    new_value = {"key": "value"}
    
    result = validator._values_different(old_value, new_value)
    assert result is False

def test_on_license_file_changed_first_time_loading(validator):
    """Test _on_license_file_changed when loading for the first time."""
    validator._last_license_data = None
    validator._license_data = None
    
    with patch.object(validator, 'validate_license', return_value=(True, "valid")):
        validator._on_license_file_changed()
    
    # Should handle first-time loading gracefully

def test_on_license_file_changed_with_changes(validator):
    """Test _on_license_file_changed when changes are detected."""
    validator._last_license_data = {"old": "data"}
    validator._license_data = {"new": "data"}
    
    with patch.object(validator, 'validate_license', return_value=(True, "valid")):
        with patch.object(validator, '_detect_changes', return_value={"field": "changed"}):
            with patch.object(validator, '_check_and_notify_status_change') as mock_notify:
                with patch.object(validator, '_store_valid_license_data'):
                    validator._on_license_file_changed()
                    mock_notify.assert_called()

def test_on_license_file_changed_no_changes(validator):
    """Test _on_license_file_changed when no changes are detected."""
    validator._last_license_data = {"same": "data"}
    validator._license_data = {"same": "data"}
    
    with patch.object(validator, 'validate_license', return_value=(True, "valid")):
        with patch.object(validator, '_detect_changes', return_value=None):
            with patch.object(validator, '_check_and_notify_status_change') as mock_notify:
                with patch.object(validator, '_store_valid_license_data'):
                    validator._on_license_file_changed()
                    mock_notify.assert_called()

def test_on_license_file_changed_validation_fails(validator):
    """Test _on_license_file_changed when validation fails."""
    validator._last_license_data = {"old": "data"}
    validator._license_data = {"new": "data"}
    
    with patch.object(validator, 'validate_license', return_value=(False, "invalid")):
        validator._on_license_file_changed()
    
    # Should handle validation failure gracefully


# --------------------------
# LicenseValidator tests
# --------------------------

def test_is_watchdog_configured_true_false(validator):
    with patch("license_lib.validator.os.path.exists", return_value=True), \
         patch("license_lib.validator.os.access", return_value=True):
        assert validator.is_watchdog_configured()
    with patch("license_lib.validator.os.path.exists", return_value=False):
        assert not validator.is_watchdog_configured()


def test_is_watchdog_configured_exception(validator):
    with patch("license_lib.validator.os.path.exists", side_effect=Exception("test")):
        assert not validator.is_watchdog_configured()


def test_is_configured(validator):
    with patch("license_lib.validator.os.path.exists", return_value=True), \
         patch("license_lib.validator.os.access", return_value=True):
        assert validator.is_configured()


def test_is_configured_license_dir_not_exists(validator):
    with patch("license_lib.validator.os.path.exists", side_effect=[False, True]), \
         patch("license_lib.validator.os.access", return_value=True):
        assert not validator.is_configured()


def test_is_configured_license_dir_not_accessible(validator):
    with patch("license_lib.validator.os.path.exists", return_value=True), \
         patch("license_lib.validator.os.access", side_effect=[False, True]):
        assert not validator.is_configured()


def test_is_configured_public_key_not_exists(validator):
    with patch("license_lib.validator.os.path.exists", side_effect=[True, False]), \
         patch("license_lib.validator.os.access", return_value=True):
        assert not validator.is_configured()


def test_is_configured_public_key_not_accessible(validator):
    with patch("license_lib.validator.os.path.exists", return_value=True), \
         patch("license_lib.validator.os.access", side_effect=[True, False]):
        assert not validator.is_configured()


def test_is_configured_exception(validator):
    with patch("license_lib.validator.os.path.exists", side_effect=Exception("test")):
        assert not validator.is_configured()


def test_stop_watchdog(validator):
    validator._watchdog_started = True
    validator._watchdog_observer = MagicMock()
    
    validator.stop_watchdog()
    
    validator._watchdog_observer.stop.assert_called_once()
    validator._watchdog_observer.join.assert_called_once()


def test_is_watchdog_running(validator):
    validator._watchdog_started = True
    assert validator.is_watchdog_running()
    
    validator._watchdog_started = False
    assert not validator.is_watchdog_running()


def test_set_status_change_callback(validator):
    def test_callback(data, reason):
        pass
    
    validator.set_status_change_callback(test_callback)
    assert validator._on_status_change == test_callback
    assert validator._previous_validation_status is None


def test_set_status_change_callback_none(validator):
    validator.set_status_change_callback(None)
    assert validator._on_status_change is None
    assert validator._previous_validation_status is None


def test_clear_cache(validator):
    validator._validation_result = (True, "test")
    validator._license_data = {"test": "data"}
    validator._public_key = MagicMock()
    
    validator.clear_cache()
    
    assert validator._validation_result is None
    assert validator._license_data is None
    assert validator._public_key is None


def test_validate_license_cached_result(validator):
    validator._validation_result = (True, "cached")
    result = validator.validate_license()
    assert result == (True, "cached")


def test_validate_license_force_refresh(validator, valid_license):
    validator._validation_result = (True, "cached")
    validator._license_data = {"old": "data"}
    
    with patch.object(validator.license_loader, '_reload_license', return_value=valid_license):
        with patch.object(validator, '_verify_signature', return_value=(True, "ok")):
            with patch.object(validator, '_check_expiration', return_value=(True, "ok")):
                with patch.object(validator, '_verify_binding', return_value=(True, "ok")):
                    result = validator.validate_license(force_refresh=True)
    
    assert result == (True, "License is valid")
    assert validator._validation_result == (True, "License is valid")


def test_validate_license_invalid_structure(validator):
    invalid_license = {"invalid": "data"}
    with patch.object(validator.license_loader, '_load_license', return_value=invalid_license):
        result = validator.validate_license()
    
    assert result == (False, "Invalid license structure")


def test_validate_license_signature_failure(validator, valid_license):
    with patch.object(validator.license_loader, '_load_license', return_value=valid_license):
        with patch.object(validator, '_verify_signature', return_value=(False, "signature failed")):
            result = validator.validate_license()
    
    assert result == (False, "signature failed")


def test_validate_license_expiration_failure(validator, valid_license):
    with patch.object(validator.license_loader, '_load_license', return_value=valid_license):
        with patch.object(validator, '_verify_signature', return_value=(True, "ok")):
            with patch.object(validator, '_check_expiration', return_value=(False, "expired")):
                result = validator.validate_license()
    
    assert result == (False, "expired")


def test_validate_license_binding_failure(validator, valid_license):
    with patch.object(validator.license_loader, '_load_license', return_value=valid_license):
        with patch.object(validator, '_verify_signature', return_value=(True, "ok")):
            with patch.object(validator, '_check_expiration', return_value=(True, "ok")):
                with patch.object(validator, '_verify_binding', return_value=(False, "binding failed")):
                    result = validator.validate_license()
    
    assert result == (False, "binding failed")


def test_validate_license_success(validator, valid_license):
    with patch.object(validator.license_loader, '_load_license', return_value=valid_license):
        with patch.object(validator, '_verify_signature', return_value=(True, "ok")):
            with patch.object(validator, '_check_expiration', return_value=(True, "ok")):
                with patch.object(validator, '_verify_binding', return_value=(True, "ok")):
                    result = validator.validate_license()
    
    assert result == (True, "License is valid")
    assert validator._validation_result == (True, "License is valid")


def test_notify_status_change_success(validator):
    callback_called = False
    def test_callback(data, reason):
        nonlocal callback_called
        callback_called = True
        assert data is True
        assert reason == "test"
    
    validator._on_status_change = test_callback
    validator._notify_status_change(True, "test")
    assert callback_called


def test_notify_status_change_exception(validator):
    def test_callback(data, reason):
        raise Exception("callback error")
    
    validator._on_status_change = test_callback
    # Should not raise exception
    validator._notify_status_change(True, "test")


def test_check_and_notify_status_change_first_time(validator):
    validator._previous_validation_status = None
    validator._notify_status_change = MagicMock()
    
    validator._check_and_notify_status_change(True, "test")
    # Should not notify on first time
    validator._notify_status_change.assert_not_called()
    assert validator._previous_validation_status is True


def test_check_and_notify_status_change_status_changed(validator):
    validator._previous_validation_status = False
    validator._notify_status_change = MagicMock()
    
    validator._check_and_notify_status_change(True, "test")
    # Should notify when status changes
    validator._notify_status_change.assert_called_once_with(True, "test")
    assert validator._previous_validation_status is True


def test_check_and_notify_status_change_with_changes(validator):
    validator._previous_validation_status = True
    validator._notify_status_change = MagicMock()
    changes = {"field": "changed"}
    
    validator._check_and_notify_status_change(True, "test", changes)
    # Should notify with changes
    validator._notify_status_change.assert_called_once_with({"changed": changes}, "test")
    assert validator._previous_validation_status is True


def test_detect_changes_no_previous_data(validator):
    new_data = {"field1": "value1"}
    changes = validator._detect_changes(new_data)
    assert changes is None


def test_detect_changes_empty_new_data(validator):
    validator._last_license_data = {"field1": "value1"}
    changes = validator._detect_changes({})
    assert changes is None


def test_detect_changes_field_added(validator):
    validator._last_license_data = {"field1": "value1"}
    new_data = {"field1": "value1", "field2": "value2"}
    changes = validator._detect_changes(new_data)
    assert "field2" in changes
    assert changes["field2"]["old"] is None
    assert changes["field2"]["new"] == "value2"


def test_detect_changes_field_removed(validator):
    validator._last_license_data = {"field1": "value1", "field2": "value2"}
    new_data = {"field1": "value1"}
    changes = validator._detect_changes(new_data)
    assert "field2" in changes
    assert changes["field2"]["old"] == "value2"
    assert changes["field2"]["new"] is None


def test_detect_changes_field_changed(validator):
    validator._last_license_data = {"field1": "value1"}
    new_data = {"field1": "value2"}
    changes = validator._detect_changes(new_data)
    assert "field1" in changes
    assert changes["field1"]["old"] == "value1"
    assert changes["field1"]["new"] == "value2"


def test_detect_changes_ignores_signature_field(validator):
    validator._last_license_data = {"field1": "value1", "signature": "old_sig"}
    new_data = {"field1": "value1", "signature": "new_sig"}
    changes = validator._detect_changes(new_data)
    assert changes is None


def test_store_valid_license_data(validator):
    license_data = {"field1": "value1"}
    validator._store_valid_license_data(license_data)
    assert validator._last_license_data == license_data
    assert validator._last_license_data is not license_data  # Should be a copy


def test_values_different_none_values(validator):
    assert not validator._values_different(None, None)
    assert validator._values_different(None, "value")
    assert validator._values_different("value", None)


def test_values_different_lists_same(validator):
    list1 = [1, 2, 3]
    list2 = [3, 1, 2]  # Same elements, different order
    assert not validator._values_different(list1, list2)


def test_values_different_lists_different(validator):
    list1 = [1, 2, 3]
    list2 = [1, 2, 4]
    assert validator._values_different(list1, list2)


def test_values_different_lists_json_error(validator):
    list1 = [{"unhashable": "object"}]
    list2 = [{"different": "object"}]
    # Should fall back to direct comparison
    assert validator._values_different(list1, list2)


def test_values_different_dicts_same(validator):
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 2, "a": 1}
    assert not validator._values_different(dict1, dict2)


def test_values_different_dicts_different_keys(validator):
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 1, "c": 3}
    assert validator._values_different(dict1, dict2)


def test_values_different_dicts_different_values(validator):
    dict1 = {"a": 1, "b": 2}
    dict2 = {"a": 1, "b": 3}
    assert validator._values_different(dict1, dict2)


def test_values_different_simple_values(validator):
    assert not validator._values_different("same", "same")
    assert validator._values_different("different", "values")
    assert validator._values_different(1, 2)


def test_start_watchdog_observer_already_started(validator):
    validator._watchdog_started = True
    validator._start_watchdog_observer()
    # Should return early without starting


def test_start_watchdog_observer_not_configured(validator):
    with patch.object(validator, 'is_watchdog_configured', return_value=False):
        validator._start_watchdog_observer()
        assert not validator._watchdog_started


def test_start_watchdog_observer_success(validator):
    with patch.object(validator, 'is_watchdog_configured', return_value=True):
        with patch('license_lib.validator.Observer') as mock_observer:
            mock_observer_instance = MagicMock()
            mock_observer.return_value = mock_observer_instance
            
            validator._start_watchdog_observer()
            
            assert validator._watchdog_started
            mock_observer_instance.schedule.assert_called_once()
            mock_observer_instance.start.assert_called_once()


def test_start_watchdog_observer_exception(validator):
    with patch.object(validator, 'is_watchdog_configured', return_value=True):
        with patch('license_lib.validator.Observer', side_effect=Exception("test")):
            validator._start_watchdog_observer()
            assert not validator._watchdog_started


def test_cleanup_watchdog_not_started(validator):
    validator._watchdog_started = False
    validator._cleanup_watchdog()
    # Should not raise exception


def test_cleanup_watchdog_success(validator):
    validator._watchdog_started = True
    validator._watchdog_observer = MagicMock()
    
    validator._cleanup_watchdog()
    
    validator._watchdog_observer.stop.assert_called_once()
    validator._watchdog_observer.join.assert_called_once()


def test_cleanup_watchdog_exception(validator):
    validator._watchdog_started = True
    validator._watchdog_observer = MagicMock()
    validator._watchdog_observer.stop.side_effect = Exception("test")
    
    # Should not raise exception
    validator._cleanup_watchdog()


def test_on_license_file_changed_success(validator, valid_license):
    old_data = {"field1": "old_value"}
    new_data = valid_license.copy()
    
    validator._last_license_data = old_data.copy()
    validator._license_data = new_data.copy()
    
    def mock_validate_license(force_refresh=False):
        # Set the license data when validate_license is called
        validator._license_data = new_data.copy()
        return (True, "valid")
    
    with patch.object(validator, 'validate_license', side_effect=mock_validate_license):
        with patch.object(validator, '_store_valid_license_data') as mock_store:
            validator._on_license_file_changed()
            
            # Should store the new data
            mock_store.assert_called_once_with(new_data)


def test_on_license_file_changed_validation_fails(validator):
    with patch.object(validator, 'validate_license', return_value=(False, "invalid")):
        with patch.object(validator, '_store_valid_license_data') as mock_store:
            validator._on_license_file_changed()
            # Should not update _last_license_data
            mock_store.assert_not_called()


def test_on_license_file_changed_exception(validator):
    with patch.object(validator, 'validate_license', side_effect=Exception("test")):
        # Should not raise exception
        validator._on_license_file_changed()


def test_load_public_key_success(validator):
    mock_key = MagicMock()
    with patch('builtins.open', mock_open(read_data=b"public_key_data")):
        with patch('license_lib.validator.serialization.load_pem_public_key', return_value=mock_key):
            result = validator._load_public_key()
    
    assert result == mock_key
    assert validator._public_key == mock_key


def test_load_public_key_file_not_found(validator):
    with patch('builtins.open', side_effect=FileNotFoundError):
        result = validator._load_public_key()
    assert result is None


def test_verify_signature_no_signature(validator):
    validator._license_data = {"field1": "value1"}
    with patch.object(validator.license_loader, '_get_signature', return_value=None):
        result = validator._verify_signature()
    assert result == (False, "License file is missing signature field")


def test_verify_signature_public_key_not_found(validator):
    validator._license_data = {"field1": "value1"}
    with patch.object(validator.license_loader, '_get_signature', return_value=b"signature"):
        with patch.object(validator, '_load_public_key', return_value=None):
            result = validator._verify_signature()
    assert "Public key file not found" in result[1]


def test_verify_signature_invalid_signature(validator):
    validator._license_data = {"field1": "value1"}
    mock_key = MagicMock()
    mock_key.verify.side_effect = Exception("Invalid signature")
    
    with patch.object(validator.license_loader, '_get_signature', return_value=b"signature"):
        with patch.object(validator, '_load_public_key', return_value=mock_key):
            result = validator._verify_signature()
    assert "Unexpected error during signature verification" in result[1]


def test_check_expiration_no_date(validator):
    validator._license_data = {}
    result = validator._check_expiration()
    assert result == (False, "License does not contain an expiration date")


def test_check_expiration_expired(validator):
    validator._license_data = {"expiration_date": "2000-01-01"}
    result = validator._check_expiration()
    assert result == (False, "License expired on 2000-01-01")


def test_check_expiration_invalid_format(validator):
    validator._license_data = {"expiration_date": "invalid-date"}
    result = validator._check_expiration()
    assert "Invalid expiration date format" in result[1]


def test_check_expiration_exception(validator):
    validator._license_data = {"expiration_date": "2025-01-01"}
    with patch('license_lib.validator.datetime') as mock_datetime:
        mock_datetime.strptime.side_effect = Exception("test")
        result = validator._check_expiration()
    assert "Unexpected error during expiration check" in result[1]


def test_verify_binding_no_binding_id(validator):
    validator._license_data = {}
    result = validator._verify_binding()
    assert result == (False, "License does not contain a binding_id - hardware binding verification is required")


def test_verify_binding_mismatch(validator):
    validator._license_data = {"binding_id": "BIND123"}
    with patch('license_lib.binding_id.generate_binding_id', return_value="DIFFERENT"):
        result = validator._verify_binding()
    assert result == (False, "System hardware binding mismatch")


def test_verify_binding_exception(validator):
    validator._license_data = {"binding_id": "BIND123"}
    # Mock generate_binding_id to raise an exception
    with patch('license_lib.validator.generate_binding_id', side_effect=Exception("test")):
        result = validator._verify_binding()
    assert result[0] is False
    assert "Unexpected error during hardware binding verification" in result[1]


def test_prepare_for_verification(validator):
    data = {"field1": "value1", "field2": None, "field3": "value3"}
    result = validator._prepare_for_verification(data)
    assert result == {"field1": "value1", "field3": "value3"}
    assert "field2" not in result


def test_get_raw_license_data_with_data(validator):
    validator._license_data = {"field1": "value1"}
    result = validator._get_raw_license_data()
    assert result == {"field1": "value1"}
    assert result is not validator._license_data  # Should be a copy


def test_get_raw_license_data_loads_data(validator):
    validator._license_data = None
    with patch.object(validator.license_loader, '_load_license', return_value={"field1": "value1"}):
        result = validator._get_raw_license_data()
    assert result == {"field1": "value1"}


def test_get_raw_license_data_load_fails(validator):
    validator._license_data = None
    with patch.object(validator.license_loader, '_load_license', side_effect=Exception("test")):
        result = validator._get_raw_license_data()
    assert result is None


def test_get_raw_license_data_no_data(validator):
    validator._license_data = None
    with patch.object(validator.license_loader, '_load_license', return_value=None):
        result = validator._get_raw_license_data()
    assert result is None


def test_get_raw_license_data_load_exception(validator):
    validator._license_data = None
    with patch.object(validator.license_loader, '_load_license', side_effect=Exception("test")):
        result = validator._get_raw_license_data()
    assert result is None

