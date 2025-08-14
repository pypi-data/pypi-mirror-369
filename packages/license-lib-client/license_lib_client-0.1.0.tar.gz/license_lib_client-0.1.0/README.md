# License Library
A Python library for secure license validation and management.
Provides license verification, feature flags, hardware binding, and real‑time file change detection.

##  Features 

### Core Capabilities
- **Secure License Validation**: RSA signature verification with PSS padding and SHA256 hashing
- **Hardware Binding**: System-specific license binding using hardware fingerprinting
- **Expiration Management**: Automatic license expiration checking
- **Feature Flags**: Granular feature access control 
- **File Monitoring**: Real-time license file change detection and automatic revalidation
- **Change Detection**: Intelligent detection of license field changes with detailed reporting

### Security Features
- **Cryptographic Signatures**: Industry-standard RSA-PSS signature verification
- **Hardware Binding**: Prevents license sharing across different systems
- **Tamper Detection**: Automatic detection of license file modifications
- **Secure Storage**: No sensitive data exposure in error messages

### Production Features
- **Thread Safety**: Full thread-safe implementation with proper locking
- **Error Handling**: Comprehensive error handling with detailed logging
- **Resource Management**: Automatic cleanup and resource management
- **Performance**: Efficient caching and validation optimization
- **Monitoring**: Built-in logging and status change callbacks

## Installation

### From PyPI (Recommended)
```bash
pip install license-lib-client
```

### From Source
```bash
git clone https://github.com/Fexo-1/license-client.git
cd license-client
pip install -e .
```

## 📁 Project Structure

```
license-client/
├── license_lib/                   # Main library package
│   ├── __init__.py                # Public API exports
│   ├── validator.py               # Core validation logic and file monitoring
│   ├── utils.py                   # License loading and structure validation
│   ├── binding_id.py              # Hardware fingerprinting and binding
│   ├── features.py                # Feature flag management 
│   ├── get_bindind_id.py          # Generate current binding ID
│   └── version.py                 # Version information
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_validator.py          # Core validation tests
│   ├── test_features.py           # Feature management tests
│   ├── test_binding.py            # Hardware binding tests
│   ├── test_license_loader.py     # Utility function tests
│   └── test_integration.py        # Integration tests
├── docs/                          # Documentation
│   ├── USER_MANUAL.md             # Comprehensive user manual
│   └── WATCHDOG.md                # Watchdog system documentation
├── pyproject.toml                 # Project configuration and dependencies
├── MANIFEST.in                    # Package manifest
├── LICENSE                        # MIT Licenses
├── README.md                      # This file
├── CHANGELOG.md                   # Version history
├── tox.ini                        # Test configuration
└── .pre-commit-config.yaml        # Pre-commit hooks configuration
```

## 🏗️ Architecture

The library is built with a modular, layered architecture:

```
license_lib/
├── validator.py      # Core validation logic and file monitoring
├── utils.py          # License loading and structure validation
├── binding_id.py     # Hardware fingerprinting and binding
├── get_bindind_id.py  # Generate current binding ID
├── features.py       # Feature flag management 
└── __init__.py       # Public API exports
```

### Key Components
- **`LicenseLoader`**: Handles license file loading and parsing
- **`LicenseValidator`**: Main validation class with file monitoring
- **`FeatureManager`**: Manages feature access 
- **`LicenseFileHandler`**: File system monitoring and change detection

## Basic Usage Example

This example demonstrates how to initialize the license validator with a status callback, check license validity and feature flags, and monitor license file changes with automatic revalidation.

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
You can get your hardware binding ID by running the module as a script:

```bash
python -m license_lib.get_binding_id
```

## 📋 License File Format

The library expects license files in JSON format with the following structure:

```json
{
  "customer_name": "Customer Name",
  "license_type": "subscription",
  "expiration_date": "2026-12-31",
  "tps_limit": 1000,
  "features": [
    "feature_a",
    "feature_b",
    "premium_feature"
  ],
  "binding_id": "hardware_fingerprint_hash",
  "license_id": "unique-license-identifier",
  "created_at": "2025-01-01T00:00:00Z",
  "version": 1,
  "status": "active",
  "signature": "base64_encoded_rsa_signature"
}
```

- `customer_name`: Customer identifier
- `license_type`: Type of license (subscription, perpetual, etc.)
- `expiration_date`: License expiration date (YYYY-MM-DD)
- `features`: Array of enabled features
- `binding_id`: Hardware binding identifier
- `license_id`: Unique license identifier
- `tps_limit`: Transactions per second limit
- `created_at`: License creation timestamp
- `version`: License format version
- `status`: License status (active, suspended, etc.)
- `signature`: RSA signature for verification

## 🔧 Configuration

### Environment Variables

```bash
# License file paths
LICENSE_PATH=/path/to/license.json
PUBLIC_KEY_PATH=/path/to/public_key.pem

# Logging
LOG_LEVEL=INFO
VERBOSE=false
```

### Logging Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔒 Security Considerations

### Signature Verification
- Uses RSA-PSS padding with SHA256 hashing
- Matches server-side signing logic exactly
- Excludes sensitive fields from signature calculation

### Hardware Binding
- Generates unique system fingerprint from:
  - MAC addresses
  - CPU information
  - System UUID
- Prevents license sharing across systems

### File Monitoring
- Real-time detection of license file changes
- Automatic revalidation on modifications
- Secure error handling without data exposure

## Module Reference

#### Constructor
```python
LicenseValidator(
    license_path: str,
    public_key_path: str,
    on_status_change: Optional[Callable] = None
)
```

#### Methods

##### `is_valid() -> bool`
Check if the license is currently valid.


##### `get_validation_reason() -> str`
Get the reason for current validation status.

### `stop_watchdog() -> None`  
Stop the file monitoring watchdog.


### FeatureManager

### Methods

#### `is_feature_enabled(feature_name: str) -> bool`
Check if a specific feature is enabled.

#### `get_enabled_features() -> List[str]`
Get a list of all enabled features.

#### `check_multiple_features(feature_names: List[str]) -> Dict[str, bool]`
Check which features are enabled from a list.


## 🔧 Troubleshooting

### Common Issues

#### License File Not Found
```bash
# Check file path and permissions
ls -la /path/to/license.json
chmod 600 /path/to/license.json
```

#### Public Key Issues
```bash
# Verify public key format
openssl rsa -pubin -in public_key.pem -text -noout
```

#### Hardware Binding Mismatch
```python
# Generate current binding ID
python -m license_lib.get_binding_id
```

#### Signature Verification Failed
- Ensure server-side signing logic matches client verification
- Check that excluded fields are consistent
- Verify JSON serialization parameters match

### Debug Mode

```python
import logging

# Enable debug logging
logging.getLogger('license_lib').setLevel(logging.DEBUG)

# Use verbose mode in tool
tool = LicenseValidatorTool(..., verbose=True)
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

### Contributing Guidelines

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Install** development dependencies: `pip install -e ".[dev]"`
4. **Install** pre-commit hooks: `pre-commit install`
5. **Make** your changes
6. **Test** your changes: `pytest`
7. **Format** your code: `pre-commit run --all-files`
8. **Commit** your changes: `git commit -m "Add amazing feature"`
9. **Push** to your branch: `git push origin feature/amazing-feature`
10. **Submit** a pull request

### Code Standards

- **Type Hints**: All functions must have type annotations
- **Docstrings**: Comprehensive docstrings for all public methods
- **Error Handling**: Proper exception handling and logging
- **Thread Safety**: Ensure thread-safe operations where needed
- **Testing**: Maintain high test coverage (>95%)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Acknowledgments

- **Cryptography**: For secure cryptographic operations
- **Watchdog**: For efficient file system monitoring
- **Python Community**: For excellent tooling and best practices

---

