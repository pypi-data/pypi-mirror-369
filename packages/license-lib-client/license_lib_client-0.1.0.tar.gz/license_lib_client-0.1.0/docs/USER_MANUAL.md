# License Library - User Manual

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Quick Start Guide](#quick-start-guide)
4. [Core Concepts](#core-concepts)
5. [Module Reference](#module-reference)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)
8. [Testing & Development](#testing--development)
9. [Best Practices](#best-practices)

## Overview

The **License Library** is a Python module that provides enterprise-grade license validation and management for software applications. It enables you to:

- **Validate software licenses** using cryptographic signatures
- **Bind licenses to specific hardware** to prevent unauthorized sharing
- **Manage feature access** based on license entitlements
- **Monitor license changes** in real-time with automatic revalidation

### Key Features

- **Secure Validation**: RSA-PSS signature verification with SHA256 hashing
- **Hardware Binding**: System-specific fingerprinting using MAC addresses, CPU info, and UUID
- **Expiration Management**: Automatic license expiration checking
- **Feature Flags**: Granular feature access control
- **File Monitoring**: Real-time license file change detection
- **Change Detection**: Intelligent field change tracking with detailed reporting
- **Thread Safety**: Full thread-safe implementation for production use

## Installation & Setup

### Prerequisites

- **Python 3.7 or higher**
- **pip** package manager
- **Access to license files and public keys**

### Installing the Module

### From PyPI (Recommended)
```bash
pip install license-lib
```

#### Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/license-client.git
cd license-client

# Install in development mode
pip install -e .
```


### Required Files

Before using the module, ensure you have:

1. **License File** (e.g., `license.json`): Contains your license information
2. **Public Key File** (e.g., `public_key.pem`): Used to verify license signatures

### File Structure

```
your-project/
├── license.json          # Your license file
├── public_key.pem        # Public key for verification
├── your_app.py           # Your application code
└── requirements.txt      # Dependencies
```

## Quick Start Guide

### Basic License Validation with Feature Checking and Change Detection

```python
import time
import os
from dotenv import load_dotenv
from license_lib.validator import LicenseValidator
from license_lib.features import FeatureManager

# Load environment variables from .env file
load_dotenv()

# Callback to handle license status changes
def my_callback(change_data, reason):
    if isinstance(change_data, bool):
        print(f"License valid? {change_data},reason {reason}")
        if not change_data:
            print(f"License became invalid: {reason}")
    else:
        print(f"License still valid. Changes detected. {change_data},reason {reason}")

def main():
    # Read paths from environment variables, provide defaults if not set
    license_path = os.getenv("LICENSE_PATH")
    public_key_path = os.getenv("PUBLIC_KEY_PATH")

    # Initialize LicenseValidator with callback
    validator = LicenseValidator(
        license_path=license_path,
        public_key_path=public_key_path,
        on_status_change=my_callback
    )

    # Initial license validation
    print("Initial license valid:", validator.is_valid())

    # Check if watchdog is running (it starts internally when license is valid)
    watchdog_running = validator.is_watchdog_running()
    print(f"Is watchdog running? {watchdog_running}")

    # Initialize FeatureManager with validator instance
    features = FeatureManager(validator)

    # Check individual features
    print("featureA enabled:", features.is_feature_enabled("featureA"))
    print("featureB enabled:", features.is_feature_enabled("featureB"))

    # Get all enabled features
    enabled = features.get_enabled_features()
    print("Enabled features:", enabled)

    # Check multiple features at once
    status = features.check_multiple_features(["featureA", "featureB"])
    print("Multiple features status:", status)

    # Keep the script running to watch license changes
    try:
        print("Monitoring license changes. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitoring...")
        validator.stop_watchdog()

if __name__ == "__main__":
    main()

```
### Get Hardware Binding ID

You can get your hardware binding ID by running the module as a script:

```bash
python -m license_lib.get_binding_id
```

## Core Concepts

### License Validation Flow

1. **File Loading**: License data is loaded from JSON file
2. **Structure Validation**: JSON format and required fields are checked
3. **Signature Verification**: RSA signature is verified using public key
4. **Expiration Check**: License expiration date is validated
5. **Hardware Binding**: System fingerprint is compared with license binding ID
6. **Feature Extraction**: Available features and limits are extracted

### Hardware Binding

The module generates a unique system identifier using:
- **MAC Addresses**: Network interface identifiers
- **CPU Information**: Processor details and capabilities
- **System UUID**: Unique machine identifier

This prevents license sharing across different systems.

### Change Detection

The module automatically monitors license file changes and:
- Detects when files are modified, created, moved, or deleted
- Compares field values to identify changes
- Triggers callbacks with detailed change information
- Automatically revalidates licenses after changes

## Module Reference

### LicenseValidator Class

The main class for license validation and management.

### Import Statement

```python
from license_lib.validator import LicenseValidator
```
#### Constructor

```python
LicenseValidator(
    license_path: str,
    public_key_path: str,
    on_status_change: Optional[Callable] = None
)
```

**Parameters:**
- `license_path`: Path to the license JSON file
- `public_key_path`: Path to the public key PEM file
- `on_status_change`: Optional callback function for status changes

#### Core Methods

##### `is_valid() -> bool`
Check if the license is currently valid.

**Returns:** `True` if valid, `False` otherwise

**Example:**
```python
if validator.is_valid():
    print("License is valid")
```


##### `get_validation_reason() -> str`
Get the reason for current validation status.

**Returns:** String describing validation result

**Example:**
```python
reason = validator.get_validation_reason()
print(f"Current status: {reason}")
```


#### File Monitoring Methods

##### `is_watchdog_running() -> bool`
Check if file monitoring is active.

**Returns:** `True` if monitoring is running

##### `stop_watchdog() -> None`
Manually stop file monitoring.

##### `is_configured() -> bool`
Check if the validator is properly configured.

**Returns:** `True` if all required files are accessible

### FeatureManager Class

### Import Statement

```python
from license_lib.features import FeatureManager
```

#### Constructor

```python
FeatureManager(validator: LicenseValidator)
```

**Parameters:**
- `validator`: Instance of LicenseValidator

#### Methods

##### `is_feature_enabled(feature_name: str) -> bool`
Check if a specific feature is enabled.

**Parameters:**
- `feature_name`: Name of the feature to check

**Returns:** `True` if feature is available

**Example:**
```python
if feature_manager.is_feature_enabled("advanced_analytics"):
    run_advanced_analytics()
```
##### get_enabled_features() -> List[str]  
Get a list of all enabled features.

**Returns:** List of feature names currently enabled

**Example:**
```python
enabled = feature_manager.get_enabled_features()
print("Enabled features:", enabled)
```

##### check_multiple_features(feature_names: List[str]) -> Dict[str, bool]  
Check which features are enabled from a list.

**Parameters:**  
- feature_names: List of feature names to check

**Returns:** Dictionary mapping feature names to boolean indicating if enabled

**Example:**
```python
features_to_check = ["dark_mode", "beta_access", "ads_enabled"]
status = feature_manager.check_multiple_features(features_to_check)
print(status)
```


### LicenseLoader Class

Handles license file loading and parsing.

#### Methods

##### `validate_license_structure(data: Dict) -> bool`
Validate license JSON structure.

**Parameters:**
- `data`: License data dictionary

**Returns:** `True` if structure is valid


### Hardware Binding Functions

#### `generate_binding_id() -> str`
Generate system fingerprint for hardware binding.

**Returns:** String containing hardware fingerprint

**Example:**
```python
from license_lib.binding_id import generate_binding_id

current_id = generate_binding_id()
print(f"Current binding ID: {current_id}")
```

#### `verify_binding_id(registered_binding_id: str) -> bool`
Verify if current system matches registered binding ID.

**Parameters:**
- `registered_binding_id`: Binding ID from license

**Returns:** `True` if binding matches

## Configuration

### Environment Variables

You can configure the module using environment variables:

```bash
# License file paths
export LICENSE_PATH="/path/to/license.json"
export PUBLIC_KEY_PATH="/path/to/public_key.pem"

# Logging configuration
export LOG_LEVEL="INFO"
export VERBOSE="false"
```

### Logging Configuration

Configure logging for your application:

```python
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configure specific logger
logger = logging.getLogger('license_lib')
logger.setLevel(logging.DEBUG)

# Add file handler
file_handler = logging.FileHandler('license.log')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)
```


## Troubleshooting

### Common Issues and Solutions

#### 1. License File Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory`

**Solution:**
```bash
# Check if file exists
ls -la license.json

# Verify path is correct
pwd
ls -la /full/path/to/license.json

```

#### 2. Public Key Issues

**Error:** `ValueError: Could not deserialize key data`

**Solution:**
```bash
# Verify public key format
openssl rsa -pubin -in public_key.pem -text -noout

# Check if it's a valid PEM file
head -1 public_key.pem  # Should start with "-----BEGIN PUBLIC KEY-----"
```

#### 3. Hardware Binding Mismatch

**Error:** `System hardware binding mismatch`

**Solution:**
```python
from license_lib.binding_id import generate_binding_id

# Generate current binding ID
current_id = generate_binding_id()
print(f"Current binding ID: {current_id}")

# Compare with license binding_id
license_data = validator._get_raw_license_data()
if license_data:
    print(f"License binding ID: {license_data.get('binding_id')}")
```

#### 4. Signature Verification Failed

**Error:** `License signature verification failed`

**Solutions:**
- Ensure server-side signing logic matches client verification
- Check that excluded fields are consistent
- Verify JSON serialization parameters match
- Confirm public key corresponds to private key used for signing

#### 5. File Monitoring Not Working

**Issue:** Changes to license file not detected

**Solutions:**
```python
# Check if monitoring is running
print(f"Watchdog running: {validator.is_watchdog_running()}")

# Check if directory is accessible
print(f"Configured: {validator.is_configured()}")

# Manually trigger validation
validator.validate_license(force_refresh=True)
```


### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging

# Enable debug logging for license library
logging.getLogger('license_lib').setLevel(logging.DEBUG)

# Enable debug logging for specific components
logging.getLogger('license_lib.validator').setLevel(logging.DEBUG)
logging.getLogger('license_lib.binding_id').setLevel(logging.DEBUG)
```


## Testing & Development

### Running Tests

#### Prerequisites

```bash
# Install testing tools
pip install pytest pytest-cov pytest-mock
```

#### Running Test Suite

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=license_lib

# Run specific test categories
pytest -m "not slow"
pytest -m integration

# Run specific test file
pytest tests/test_validator.py

# Run with verbose output
pytest -v
```

#### Test Structure

```
tests/
├── test_validator.py      # Core validation tests
├── test_features.py       # Feature management tests
├── test_binding.py        # Hardware binding tests
├── test_license_loader.py # Utility function tests
└── test_integration.py    # Integration tests
```
## Best Practices

- **Always provide a status change callback** to react to license state changes.
- **Validate license files and public keys before deployment** to ensure they are correct and in the proper format.
- **Monitor logs at DEBUG level** during troubleshooting for detailed information.
- **Use environment variables or config files** to manage license file and key paths for flexibility.
- **Test license changes and reload scenarios in development** to ensure the system behaves as expected before going to production.

