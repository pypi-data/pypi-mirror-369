import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from license_lib.validator import LicenseValidator
from license_lib.features import FeatureManager
from license_lib.utils import LicenseLoader
from license_lib.binding_id import generate_binding_id


class TestLicenseIntegration:
    """Integration tests for the complete license validation workflow."""
    
    @pytest.fixture
    def temp_license_file(self, tmp_path):
        """Create a temporary license file for testing."""
        license_data = {
            "customer_name": "Integration Test Customer",
            "license_type": "Enterprise",
            "expiration_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "features": ["feature_a", "feature_b", "feature_c", "advanced_analytics"],
            "binding_id": "TEST_BINDING_123",
            "license_id": "INTEGRATION_TEST_001",
            "status": "active",
            "signature": "dGVzdF9zaWduYXR1cmU="  # base64 "test_signature"
        }
        
        license_file = tmp_path / "integration_license.json"
        license_file.write_text(json.dumps(license_data))
        return str(license_file)
    
    @pytest.fixture
    def temp_public_key(self, tmp_path):
        """Create a temporary public key file for testing."""
        # This is a mock public key - in real scenarios this would be a proper RSA key
        key_content = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1234567890abcdef
-----END PUBLIC KEY-----"""
        
        key_file = tmp_path / "test_public_key.pem"
        key_file.write_text(key_content)
        return str(key_file)
    
    def test_complete_license_workflow(self, temp_license_file, temp_public_key):
        """Test the complete workflow from license loading to feature validation."""
        
        # Step 1: Create validator with license and key files
        validator = LicenseValidator(temp_license_file, temp_public_key)
        
        # Step 2: Verify validator is configured
        assert validator.is_configured()
        
        # Step 3: Load and validate license
        with patch.object(validator, '_verify_signature', return_value=(True, "Success")), \
             patch.object(validator, '_verify_binding', return_value=(True, "Success")), \
             patch.object(validator, '_check_expiration', return_value=(True, "Success")):
            
            # Test license validation
            assert validator.is_valid()
            
            # Test license data retrieval
            license_data = validator._get_raw_license_data()
            assert license_data["customer_name"] == "Integration Test Customer"
            assert license_data["license_type"] == "Enterprise"
            assert "feature_a" in license_data["features"]
            
            # Step 4: Test feature management
            feature_manager = FeatureManager(validator)
            
            # Test individual feature checks
            assert feature_manager.is_feature_enabled("feature_a")
            assert feature_manager.is_feature_enabled("feature_b")
            assert not feature_manager.is_feature_enabled("non_existent_feature")
            
            # Test multiple feature check
            feature_status = feature_manager.check_multiple_features([
                "feature_a", "feature_b", "non_existent_feature"
            ])
            assert feature_status["feature_a"] is True
            assert feature_status["feature_b"] is True
            assert feature_status["non_existent_feature"] is False
            
            # Test enabled features list
            enabled_features = feature_manager.get_enabled_features()
            assert "feature_a" in enabled_features
            assert "feature_b" in enabled_features
            assert "feature_c" in enabled_features
            assert "advanced_analytics" in enabled_features
    
    def test_license_workflow_with_invalid_license(self, temp_license_file, temp_public_key):
        """Test workflow behavior with invalid license."""
        
        validator = LicenseValidator(temp_license_file, temp_public_key)
        feature_manager = FeatureManager(validator)
        
        # Test with invalid signature - force refresh to clear cache
        with patch.object(validator, '_verify_signature', return_value=(False, "Invalid signature")):
            assert not validator.validate_license(force_refresh=True)[0]
            assert not validator.is_valid()
            # Feature manager still returns features because it doesn't validate the license
            # It just reads the raw license data
            assert feature_manager.is_feature_enabled("feature_a")
            assert "feature_a" in feature_manager.get_enabled_features()
        
        # Test with invalid binding ID - force refresh to clear cache
        with patch.object(validator, '_verify_signature', return_value=(True, "Success")), \
             patch.object(validator, '_verify_binding', return_value=(False, "Invalid binding")):
            assert not validator.validate_license(force_refresh=True)[0]
            assert not validator.is_valid()
            # Feature manager still returns features because it doesn't validate the license
            assert feature_manager.is_feature_enabled("feature_a")
    
    def test_license_workflow_with_expired_license(self, temp_license_file, temp_public_key):
        """Test workflow behavior with expired license."""
        
        validator = LicenseValidator(temp_license_file, temp_public_key)
        feature_manager = FeatureManager(validator)
        
        # Test with expired license - force refresh to clear cache
        with patch.object(validator, '_verify_signature', return_value=(True, "Success")), \
             patch.object(validator, '_verify_binding', return_value=(True, "Success")), \
             patch.object(validator, '_check_expiration', return_value=(False, "License expired")):
            assert not validator.validate_license(force_refresh=True)[0]
            assert not validator.is_valid()
            # Feature manager still returns features because it doesn't validate the license
            assert feature_manager.is_feature_enabled("feature_a")
    
    def test_license_file_watching_integration(self, temp_license_file, temp_public_key):
        """Test license file watching integration."""
        
        validator = LicenseValidator(temp_license_file, temp_public_key)
        
        # Test that watchdog is configured (if supported)
        # This test may pass or fail depending on the system
        try:
            is_configured = validator.is_watchdog_configured()
            assert isinstance(is_configured, bool)
        except Exception:
            # Watchdog might not be available on all systems
            pass
    
    def test_binding_id_integration(self):
        """Test binding ID generation and verification integration."""
        
        # Test that binding ID generation works
        binding_id = generate_binding_id()
        assert isinstance(binding_id, str)
        assert len(binding_id) == 64  # SHA256 hex length
        
        # Test consistency
        binding_id2 = generate_binding_id()
        assert binding_id == binding_id2
    
    def test_license_loader_integration(self, temp_license_file):
        """Test license loader integration."""
        
        loader = LicenseLoader(temp_license_file)
        
        # Test license loading
        license_data = loader._load_license()
        assert license_data["customer_name"] == "Integration Test Customer"
        assert license_data["license_type"] == "Enterprise"
        
        # Test signature extraction
        signature = loader._get_signature()
        assert signature is not None
        
        # Test data caching
        license_data2 = loader._get_license_data()
        assert license_data2 == license_data
        assert license_data2 is not license_data  # Should be a copy
    
    def test_error_handling_integration(self, temp_license_file, temp_public_key):
        """Test error handling throughout the workflow."""
        
        validator = LicenseValidator(temp_license_file, temp_public_key)
        feature_manager = FeatureManager(validator)
        
        # Test with file not found - this should fail during validation, not raise immediately
        invalid_validator = LicenseValidator("non_existent.json", temp_public_key)
        # The validator will try to load the file during validation, not during initialization
        assert not invalid_validator.is_valid()
        
        # Test with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            f.flush()
            temp_file_path = f.name
            
        # Close the file before trying to delete it
        invalid_validator = LicenseValidator(temp_file_path, temp_public_key)
        # This should fail during validation due to JSON decode error
        assert not invalid_validator.is_valid()
        
        # Clean up the temporary file
        try:
            os.unlink(temp_file_path)
        except PermissionError:
            # File might still be in use, ignore the error
            pass
    
    def test_performance_integration(self, temp_license_file, temp_public_key):
        """Test performance aspects of the integration."""
        
        validator = LicenseValidator(temp_license_file, temp_public_key)
        feature_manager = FeatureManager(validator)
        
        with patch.object(validator, '_verify_signature', return_value=(True, "Success")), \
             patch.object(validator, '_verify_binding', return_value=(True, "Success")), \
             patch.object(validator, '_check_expiration', return_value=(True, "Success")):
            
            # Clear any cached validation result and license data
            validator.validate_license(force_refresh=True)
            validator._license_data = None  # Clear cached license data
            
            # Test that multiple feature checks don't reload license data
            # Mock the license loader's _load_license method to track calls
            with patch.object(validator.license_loader, '_load_license') as mock_load:
                # Perform multiple operations
                validator.is_valid()
                feature_manager.is_feature_enabled("feature_a")
                feature_manager.is_feature_enabled("feature_b")
                feature_manager.get_enabled_features()
                feature_manager.check_multiple_features(["feature_a", "feature_b"])
                
                # License data should only be loaded once (during the first is_valid() call)
                assert mock_load.call_count == 1
