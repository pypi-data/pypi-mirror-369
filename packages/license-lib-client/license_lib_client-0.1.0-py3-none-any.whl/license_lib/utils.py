import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LicenseLoader:
    """Handles loading and parsing of license files."""

    def __init__(self, license_path: str = "license/license.json"):
        self._license_path = license_path
        self._license_data: Optional[Dict[str, Any]] = None
        self._signature: Optional[bytes] = None

    def _load_license(self) -> Dict[str, Any]:
        """
        Load license data from file.

        Returns:
            Dict containing license data without signature

        Raises:
            FileNotFoundError: If license file doesn't exist
            json.JSONDecodeError: If license file is invalid JSON
        """
        if self._license_data is not None:
            return self._license_data.copy()

        try:
            with open(self._license_path, 'r') as f:
                license_json = json.load(f)

            # Extract signature if present
            if "signature" in license_json:
                import base64, binascii
                try:
                    self._signature = base64.b64decode(license_json["signature"])
                except binascii.Error as e:
                    logger.error(f"Invalid license format: signature is not valid Base64 ({e})")
                    raise ValueError(f"Invalid license format: signature is not valid Base64 ({e})")

            self._license_data = license_json
            logger.info(f"License loaded successfully from {self._license_path}")
            return self._license_data.copy()

        except FileNotFoundError:
            logger.error(f"License file not found: {self._license_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in license file: {e}")
            raise

    def _get_signature(self) -> Optional[bytes]:
        """Get the license signature if available."""
        if self._signature is None:
            try:
                self._load_license()
            except Exception:
                pass
        return self._signature

    def _get_license_data(self) -> Optional[Dict[str, Any]]:
        """Get the current license data."""
        return self._license_data.copy() if self._license_data else None

    def _reload_license(self) -> Dict[str, Any]:
        """Force reload of license file."""
        self._license_data = None
        self._signature = None
        return self._load_license()

    @staticmethod
    def validate_license_structure(license_data: Dict[str, Any]) -> bool:
        """
        Validate that license data has required fields.

        Args:
            license_data: License data dictionary

        Returns:
            True if structure is valid, False otherwise
        """
        required_fields = [
            "customer_name", "license_type", "expiration_date", "features",
            "binding_id", "license_id", "status","signature"
        ]

        for field in required_fields:
            if field not in license_data:
                logger.error(f"Missing required field in license: {field}")
                return False

        # Validate features structure
        if not isinstance(license_data.get("features"), list):
            logger.error("features field must be a list")
            return False

        return True

    @staticmethod
    def get_license_info(license_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract basic license information.

        Args:
            license_data: License data dictionary

        Returns:
            Dictionary with basic license info
        """
        return {
            "customer_name": license_data.get("customer_name"),
            "license_type": license_data.get("license_type"),
            "expiration_date": license_data.get("expiration_date"),
            "features": license_data.get("features", {}),
            "tps_limit": license_data.get("tps_limit"),
            "binding_id": license_data.get("binding_id"),
            "license_id": license_data.get("license_id"),
            "created_at": license_data.get("created_at"),
            "version": license_data.get("version"),
            "status": license_data.get("status"),
            # "key_id": license_data.get("key_id"),
            "signature": license_data.get("signature"),
        }
