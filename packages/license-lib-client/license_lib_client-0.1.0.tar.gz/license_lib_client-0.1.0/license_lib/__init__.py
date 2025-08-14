"""
License Library - A clean, modular license validation and management system.

This package provides license validation, feature flag checking, TPS limiting,
and hardware binding capabilities without any web framework dependencies.
"""

from .validator import LicenseValidator
from .features import FeatureManager
from .utils import LicenseLoader

from .version import __version__
__author__ = "License Library Team"

__all__ = [
    "LicenseValidator",
    "FeatureManager",
    "LicenseLoader"
] 