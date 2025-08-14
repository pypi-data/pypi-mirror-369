import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class FeatureManager:
    def __init__(self, license_validator):
        self.validator = license_validator
        self._features_cache: Optional[List[str]] = None
        self._last_license_data: Optional[dict] = None

    def _get_features(self) -> List[str]:
        """Get features list from license data with caching."""
        # Get license data directly without validation checks
        license_data = self.validator._get_raw_license_data()
        if license_data != self._last_license_data:
            self._features_cache = license_data.get("features", []) if license_data else []
            self._last_license_data = license_data
        return self._features_cache or []


    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a specific feature is enabled."""
        try:
            features = self._get_features()
            return feature_name in features
        except Exception as e:
            logger.error(f"Error checking feature '{feature_name}': {e}")
            return False

    def get_enabled_features(self) -> List[str]:
        """Returns a list of all enabled features from the license."""
        try:
            return self._get_features()
        except Exception as e:
            logger.error(f"Error getting enabled features: {e}")
            return []

    def check_multiple_features(self, feature_names: List[str]) -> dict[str, bool]:
        """Returns a dictionary indicating which of the given features are enabled."""
        try:
            features = self._get_features()
            return {name: name in features for name in feature_names}
        except Exception as e:
            logger.error(f"Error checking multiple features: {e}")
            return {}
