import json
import logging
import os
import atexit
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, Callable, Union
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from license_lib.utils import LicenseLoader
from license_lib.binding_id import generate_binding_id

logger = logging.getLogger(__name__)

# Fields to ignore during change detection (sensitive fields)
# Also includes fields excluded during server-side signing
IGNORED_FIELDS = {"binding_id", "license_id", "signature", "_id", "idempotency_key"}

# TODO: Future Enhancements
# 1. Add support for online license validation via HTTP/HTTPS
# 2. Implement WebSocket-based real-time license updates
# 3. Add support for license polling from remote servers
# 4. Implement license caching with TTL for offline scenarios
# 5. Add support for multiple license files and failover
# 6. Implement license usage tracking and reporting


class LicenseFileHandler(FileSystemEventHandler):
    """Watches for changes to the license file and triggers revalidation."""

    def __init__(self, license_validator, license_path: str):
        self.license_validator = license_validator
        # Normalize and absolute path for reliable matching
        self.license_path = os.path.abspath(license_path)
        self._last_validation_time = 0
        self._cooldown_seconds = 1  # Prevent multiple rapid validations

    def _is_license_file(self, event_path: str) -> bool:
        # Compare absolute normalized paths
        return os.path.abspath(event_path) == self.license_path

    def on_modified(self, event):
        if not event.is_directory and self._is_license_file(event.src_path):
            current_time = time.time()
            if current_time - self._last_validation_time > self._cooldown_seconds:
                logger.info(f"License file modified: {event.src_path}")
                logger.debug(f"File modification detected, triggering change handler")
                self._handle_change()
                self._last_validation_time = current_time
            else:
                logger.debug(f"File modification ignored due to cooldown: {current_time - self._last_validation_time:.2f}s remaining")
        else:
            logger.debug(f"File modification event ignored: is_directory={event.is_directory}, path={event.src_path}")

    def on_created(self, event):
        if not event.is_directory and self._is_license_file(event.src_path):
            logger.info(f"License file created: {event.src_path}")
            self._handle_change()

    def on_moved(self, event):
        if not event.is_directory and self._is_license_file(event.dest_path):
            logger.info(f"License file moved to: {event.dest_path}")
            self._handle_change()

    def on_deleted(self, event):
        if not event.is_directory and self._is_license_file(event.src_path):
            logger.warning(f"License file deleted: {event.src_path}")
            self._handle_change()

    def _handle_change(self):
        """Handle license file changes by triggering revalidation."""
        logger.debug("File change handler triggered, attempting to reload license")
        for attempt in range(5):
            try:
                logger.debug(f"Attempt {attempt + 1}/5: calling _on_license_file_changed")
                self.license_validator._on_license_file_changed()
                logger.debug("File change handled successfully")
                break  # Success, exit retry loop
            except json.JSONDecodeError:
                # Likely file is still being written, wait and retry
                logger.debug(f"JSON decode error on attempt {attempt + 1}, retrying...")
                time.sleep(0.2)
            except Exception as e:
                logger.error(f"Unexpected error during license file change handling: {e}")
                break  # Exit on unexpected errors
        else:
            logger.error("Failed to reload license file after multiple retries")


class LicenseValidator:
    """
    Handles license validation, signature verification, and hardware binding.
    
    This class provides comprehensive license management including:
    - Cryptographic signature verification
    - Hardware binding validation
    - Expiration checking
    - Real-time file monitoring
    - Change detection and notification
    """

    def __init__(self, license_path: str = "license/license.json",
                 public_key_path: str = "keys/public_key.pem",
                 on_status_change: Optional[Callable[[Union[bool, Dict[str, Any]], str], None]] = None):
        """
        Initialize the license validator.
        
        Args:
            license_path: Path to the license JSON file
            public_key_path: Path to the public key PEM file
            on_status_change: Optional callback for status change notifications
        """
        if not license_path:
            raise ValueError("license_path cannot be empty")
        if not public_key_path:
            raise ValueError("public_key_path cannot be empty")
            
        self.license_loader = LicenseLoader(license_path)
        self.public_key_path = public_key_path
        self._license_data: Optional[Dict[str, Any]] = None
        self._validation_result: Optional[Tuple[bool, str]] = None
        
        # Status change notification callback
        self._on_status_change = on_status_change
        self._previous_validation_status: Optional[bool] = None
        
        # Change detection: stored copy of previous license data
        self._last_license_data: Optional[Dict[str, Any]] = None

        # Watchdog observer for license file monitoring
        self._watchdog_observer: Optional[Observer] = None
        self._watchdog_started = False
        self._license_path = os.path.abspath(license_path)

        # Lock for thread-safe access to validation state and change detection
        self._lock = threading.RLock()

        # Cache for loaded public key
        self._public_key = None

        # Register cleanup on exit
        atexit.register(self._cleanup_watchdog)



    def is_valid(self) -> bool:
        """
        Check if license is currently valid.
        
        Returns:
            True if license is valid, False otherwise
        """
        is_valid, _ = self.validate_license()

        # Start watchdog observer when license becomes valid for the first time
        if is_valid and not self._watchdog_started:
            self._start_watchdog_observer()

        return is_valid

    def get_validation_reason(self) -> str:
        """
        Get the reason for current validation status.
        
        Returns:
            String describing the validation result
        """
        _, reason = self.validate_license()
        return reason

    def refresh_validation(self) -> Tuple[bool, str]:
        """
        Force refresh of license validation by reloading from disk.
        
        Returns:
            Tuple of (is_valid, reason)
        """
        return self.validate_license(force_refresh=True)

    def set_status_change_callback(self, callback: Optional[Callable[[Union[bool, Dict[str, Any]], str], None]]) -> None:
        """
        Set or update the status change callback.
        
        Args:
            callback: Function to call when license status changes.
                     Should accept (data: Union[bool, Dict[str, Any]], reason: str) parameters.
                     Pass None to remove the callback.
        """
        with self._lock:
            self._on_status_change = callback
            # Reset previous status to ensure next validation triggers callback
            self._previous_validation_status = None
            logger.info("Status change callback updated")

    def clear_cache(self) -> None:
        """Clear the validation cache to force reload on next validation."""
        with self._lock:
            self._validation_result = None
            self._license_data = None
            self._public_key = None

    # ============================================================================
    # Watchdog/File Monitoring Methods
    # ============================================================================

    def stop_watchdog(self):
        """Manually stop the watchdog observer."""
        self._cleanup_watchdog()

    def is_watchdog_running(self) -> bool:
        """Check if the watchdog observer is currently running."""
        return self._watchdog_started
    
    def is_watchdog_configured(self) -> bool:
        """Check if the watchdog can be started (directory exists and accessible)."""
        try:
            license_dir = os.path.dirname(self._license_path)
            return os.path.exists(license_dir) and os.access(license_dir, os.R_OK)
        except Exception:
            return False
    
    def is_configured(self) -> bool:
        """Check if the validator is properly configured with required files."""
        try:
            # Check if license file directory exists and is accessible
            license_dir = os.path.dirname(self._license_path)
            if not os.path.exists(license_dir) or not os.access(license_dir, os.R_OK):
                return False
            
            # Check if public key file exists and is accessible
            if not os.path.exists(self.public_key_path) or not os.access(self.public_key_path, os.R_OK):
                return False
            
            return True
        except Exception:
            return False

    # ============================================================================
    # Core Validation Methods
    # ============================================================================

    def validate_license(self, force_refresh: bool = False) -> Tuple[bool, str]:
        """
        Perform complete license validation including signature and hardware binding.

        Args:
            force_refresh: If True, force reload license data from disk

        Returns:
            Tuple of (is_valid, reason)
        """
        with self._lock:
            if force_refresh:
                self._validation_result = None
                self._license_data = None

            if self._validation_result is not None:
                return self._validation_result

            try:
                # Load license data (force reload if requested)
                if force_refresh:
                    self._license_data = self.license_loader._reload_license()
                else:
                    self._license_data = self.license_loader._load_license()

                # Validate structure
                if not LicenseLoader.validate_license_structure(self._license_data):
                    self._validation_result = (False, "Invalid license structure")
                    self._check_and_notify_status_change(False, "Invalid license structure")
                    return self._validation_result

                # Verify signature
                signature_valid, signature_reason = self._verify_signature()
                if not signature_valid:
                    self._validation_result = (False, signature_reason)
                    self._check_and_notify_status_change(False, signature_reason)
                    return self._validation_result

                # Check expiration
                expiry_valid, expiry_reason = self._check_expiration()
                if not expiry_valid:
                    self._validation_result = (False, expiry_reason)
                    self._check_and_notify_status_change(False, expiry_reason)
                    return self._validation_result

                # Verify hardware binding
                binding_valid, binding_reason = self._verify_binding()
                if not binding_valid:
                    self._validation_result = (False, binding_reason)
                    self._check_and_notify_status_change(False, binding_reason)
                    return self._validation_result

                self._validation_result = (True, "License is valid")
                logger.info("License validation successful")
                
                # Store valid license data for change detection
                self._store_valid_license_data(self._license_data)
                
                # Check for status change and notify callback
                self._check_and_notify_status_change(True, "License is valid")
                
                return self._validation_result

            except ValueError as e:
                # Special handling for Base64 decode and similar ValueErrors
                self._validation_result = (False, str(e))
                self._check_and_notify_status_change(False, str(e))
                return self._validation_result

            except Exception as e:
                error_msg = f"Unexpected error during license validation: {e}"
                logger.exception(error_msg)
                self._validation_result = (False, error_msg)
                self._check_and_notify_status_change(False, error_msg)
                return self._validation_result

    # ============================================================================
    # Private Helper Methods
    # ============================================================================

    def _notify_status_change(self, data: Union[bool, Dict[str, Any]], reason: str) -> None:
        """Notify the callback about status changes if callback is provided."""
        if self._on_status_change is not None:
            try:
                self._on_status_change(data, reason)
                logger.debug(f"Status change notification sent: data={data}, reason='{reason}'")
            except Exception as e:
                logger.error(f"Error in status change callback: {e}")

    def _check_and_notify_status_change(self, is_valid: bool, reason: str, changes: Optional[Dict[str, Any]] = None) -> None:
        """Check if status has changed and notify callback if it has."""
        if self._previous_validation_status is not None and self._previous_validation_status != is_valid:
            # Status has changed, notify callback
            self._notify_status_change(is_valid, reason)
        elif is_valid and changes:
            # License is still valid but has changes, notify callback with changes
            self._notify_status_change({"changed": changes}, reason)
        
        # Update previous status
        self._previous_validation_status = is_valid

    def _detect_changes(self, new_license_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect changes between new license data and previous valid license data.
        Only stores valid license data for comparison.
        
        Args:
            new_license_data: The newly loaded license data
            
        Returns:
            Dictionary describing changes, or None if no changes detected
        """
        if not new_license_data:
            logger.warning("Cannot detect changes: new license data is empty")
            return None
            
        with self._lock:
            if self._last_license_data is None:
                # First time loading, store the data and return None (no changes)
                self._last_license_data = new_license_data.copy()
                logger.debug("First time loading license data, no changes to detect")
                return None
            
            logger.debug(f"Comparing license data - old keys: {len(self._last_license_data)} fields, new keys: {len(new_license_data)} fields")
            
            changes = {}
            
            # Check for added fields (keys in new but not in old)
            for key in new_license_data:
                if key not in IGNORED_FIELDS and key not in self._last_license_data:
                    changes[key] = {"old": None, "new": new_license_data[key]}
                    logger.debug(f"Field added: {key}")
            
            # Check for removed fields (keys in old but not in new)
            for key in self._last_license_data:
                if key not in IGNORED_FIELDS and key not in new_license_data:
                    changes[key] = {"old": self._last_license_data[key], "new": None}
                    logger.debug(f"Field removed: {key}")
            
            # Check for changed fields (keys in both)
            for key in self._last_license_data:
                if key not in IGNORED_FIELDS and key in new_license_data:
                    old_value = self._last_license_data[key]
                    new_value = new_license_data[key]
                    if self._values_different(old_value, new_value):
                        changes[key] = {"old": old_value, "new": new_value}
                        logger.debug(f"Field changed: {key}")
            
            # Don't update stored license data here - it's managed separately
            # by _store_valid_license_data when validation succeeds
            
            logger.debug(f"Change detection completed. Found {len(changes)} changes: {list(changes.keys()) if changes else 'None'}")
            return changes if changes else None

    def _store_valid_license_data(self, license_data: Dict[str, Any]) -> None:
        """
        Store a copy of valid license data for change detection.
        This method is called when a license is successfully validated.
        
        Args:
            license_data: The validated license data to store
        """
        with self._lock:
            self._last_license_data = license_data.copy()
            logger.debug(f"Stored valid license data for change detection: {len(license_data)} fields")

    def _values_different(self, old_value: Any, new_value: Any) -> bool:
        """
        Compare two values to determine if they are different.
        Handles special cases like lists (compared as sets) and nested objects.
        
        Args:
            old_value: Previous value
            new_value: New value
            
        Returns:
            True if values are different, False otherwise
        """
        # Handle None cases
        if old_value is None and new_value is None:
            return False
        if old_value is None or new_value is None:
            return True
        
        # Handle lists - compare as sets (order doesn't matter)
        if isinstance(old_value, list) and isinstance(new_value, list):
            try:
                # Convert to sets for comparison, handling non-hashable elements
                old_set = set(json.dumps(item, sort_keys=True) for item in old_value)
                new_set = set(json.dumps(item, sort_keys=True) for item in new_value)
                result = old_set != new_set
                logger.debug(f"List comparison result: different={result}")
                return result
            except (TypeError, ValueError):
                # Fallback to direct comparison if JSON serialization fails
                result = old_value != new_value
                logger.debug(f"List comparison fallback result: different={result}")
                return result
        
        # Handle dictionaries - recursive comparison
        if isinstance(old_value, dict) and isinstance(new_value, dict):
            if len(old_value) != len(new_value):
                return True
            
            for key in old_value:
                if key not in new_value:
                    return True
                if self._values_different(old_value[key], new_value[key]):
                    return True
            return False
        
        # Default comparison for other types
        return old_value != new_value

    def _start_watchdog_observer(self):
        """Start the watchdog observer to monitor license file changes."""
        if self._watchdog_started:
            return

        try:
            # Check if watchdog can be configured before starting
            if not self.is_watchdog_configured():
                logger.warning("Cannot start watchdog - directory not accessible")
                return

            # Get the directory containing the license file
            license_dir = os.path.dirname(self._license_path)

            # Create handler and schedule it
            handler = LicenseFileHandler(self, self._license_path)
            self._watchdog_observer = Observer()
            self._watchdog_observer.schedule(handler, path=license_dir, recursive=False)

            # Start the observer
            self._watchdog_observer.start()
            self._watchdog_started = True

            logger.info(f"Watchdog license monitor started. Watching: {self._license_path}")
            logger.info(f"Monitoring directory: {license_dir}")
            logger.debug(f"Watchdog observer status: {self._watchdog_observer.is_alive()}")

        except Exception as e:
            logger.error(f"Failed to start watchdog monitor: {e}")
            # Don't raise - watchdog failure shouldn't break license validation

    def _cleanup_watchdog(self):
        """Clean up watchdog observer on exit."""
        if self._watchdog_observer and self._watchdog_started:
            try:
                self._watchdog_observer.stop()
                self._watchdog_observer.join()
                logger.info("Watchdog license monitor stopped.")
            except Exception as e:
                logger.error(f"Error stopping watchdog monitor: {e}")

    def _on_license_file_changed(self):
        """Handle license file changes by reloading and revalidating."""
        try:
            logger.info("License file changed, reloading and revalidating...")
            logger.debug(f"Current _last_license_data fields: {len(self._last_license_data) if self._last_license_data else 0}")
            logger.debug(f"Current _license_data fields: {len(self._license_data) if self._license_data else 0}")

            # PRESERVE the old license data for change detection BEFORE validation
            old_license_data = self._last_license_data.copy() if self._last_license_data else None
            logger.debug(f"Preserved old license data for comparison: {len(old_license_data) if old_license_data else 0} fields")

            with self._lock:
                # Clear cached validation results to force revalidation
                self._validation_result = None
                self._license_data = None
                self._public_key = None 

            # Revalidate the license
            is_valid, reason = self.validate_license(force_refresh=True)

            if is_valid:
                logger.info("License revalidation successful after file change")
                
                # TEMPORARILY restore old data for change detection
                if old_license_data:
                    temp_last_license_data = self._last_license_data
                    self._last_license_data = old_license_data
                    
                    # Detect changes in license data compared to previous valid state
                    changes = self._detect_changes(self._license_data)
                    logger.debug(f"Change detection result: {changes}")
                    
                    # Restore the new data
                    self._last_license_data = temp_last_license_data
                else:
                    # First time loading, no changes to detect
                    changes = None
                    logger.debug("First time loading license data, no changes to detect")
                
                # Store the valid license data for future change detection
                self._store_valid_license_data(self._license_data)
                
                if changes:
                    logger.info(f"License fields changed: {list(changes.keys())}")
                    # Notify callback about field changes using _check_and_notify_status_change
                    self._check_and_notify_status_change(True, "License is valid", changes)
                else:
                    logger.info("No license field changes detected")
                    # Send standard validity update when no changes
                    self._check_and_notify_status_change(True, "License is valid")
            else:
                logger.warning(f"License revalidation failed after file change: {reason}")

        except Exception as e:
            logger.error(f"Error during license file change handling: {e}")

    def _load_public_key(self):
        """Load and cache the public key."""
        if self._public_key is not None:
            return self._public_key

        try:
            with open(self.public_key_path, 'rb') as f:
                self._public_key = serialization.load_pem_public_key(f.read())
            logger.info(f"Loaded public key from {self.public_key_path}")
            return self._public_key
        except FileNotFoundError:
            logger.error(f"Public key file not found: {self.public_key_path}")
            return None
        except Exception as e:
            logger.error(f"Error loading public key: {e}")
            return None

    def _verify_signature(self) -> Tuple[bool, str]:
        """
        Verify license signature using public key.

        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            signature = self.license_loader._get_signature()
            if signature is None:
                return False, "License file is missing signature field"

            # Prepare payload for verification - match server-side signing logic exactly
            # Exclude the same fields that the server excludes during signing
            data_to_verify = {
                k: v
                for k, v in self._license_data.items()
                if k not in ("signature", "_id", "idempotency_key")
            }
            
            # Apply the same preparation logic as server-side
            data_to_verify = self._prepare_for_verification(data_to_verify)
            
            # Use the same JSON serialization as server-side
            payload = json.dumps(data_to_verify, sort_keys=True, separators=(",", ":")).encode()

            # Load cached public key
            public_key = self._load_public_key()
            if public_key is None:
                return False, f"Public key file not found or could not be loaded: {self.public_key_path}"

            # Verify signature using PSS padding to match license creation side
            public_key.verify(
                signature,
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True, "Signature verification successful"

        except InvalidSignature:
            return False, "License signature verification failed - license may be tampered"
        except ValueError as e:
            return False, f"Signature verification failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during signature verification: {str(e)}"

    def _check_expiration(self) -> Tuple[bool, str]:
        """
        Check if license has expired.

        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            expiry_str = self._license_data.get("expiration_date")
            if not expiry_str:
                return False, "License does not contain an expiration date"

            expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
            if datetime.now() >= expiry:
                return False, f"License expired on {expiry_str}"

            return True, "License is not expired"

        except ValueError as e:
            return False, f"Invalid expiration date format: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during expiration check: {str(e)}"

    def _verify_binding(self) -> Tuple[bool, str]:
        """
        Verify hardware binding.

        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            registered_binding_id = self._license_data.get("binding_id")
            if not registered_binding_id:
                return False, "License does not contain a binding_id - hardware binding verification is required"

            current_binding_id = generate_binding_id().strip().upper()
            registered_binding_id = registered_binding_id.strip().upper()

            if current_binding_id != registered_binding_id:
                logger.warning("Hardware binding mismatch detected")
                return False, "System hardware binding mismatch"

            logger.info("Hardware binding verification successful")
            return True, "Hardware binding verification successful"

        except Exception as e:
            return False, f"Unexpected error during hardware binding verification: {str(e)}"

    def _prepare_for_verification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare data for verification - matches server-side prepare_for_signing logic.
        
        This method should implement the same data preparation logic that the server
        uses before signing. If you have access to the server-side prepare_for_signing
        function, copy its logic here exactly.
        
        Args:
            data: License data to prepare for verification
            
        Returns:
            Prepared data ready for signature verification
        """
        
        prepared_data = data.copy()
        
        prepared_data = {k: v for k, v in prepared_data.items() if v is not None}
        
        return prepared_data
    
    def _get_raw_license_data(self) -> Optional[Dict[str, Any]]:
        """
        Get raw license data without validation - for internal feature checking.
        
        This method is private and should only be used internally by FeatureManager
        to access license data without going through validation checks.
        
        Returns:
            Dictionary containing license information or None if not available
        """
        with self._lock:
            if self._license_data is None:
                # Try to load license data directly from loader
                try:
                    self._license_data = self.license_loader._load_license()
                except Exception as e:
                    logger.warning(f"Could not load raw license data: {e}")
                    return None
            return self._license_data.copy() if self._license_data else None
