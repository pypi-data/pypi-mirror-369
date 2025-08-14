import platform
import subprocess
import uuid
import hashlib
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _get_mac_address() -> Optional[str]:
    """
    Get the MAC address of the primary network interface.
    
    Returns:
        MAC address string or None if unavailable
    """
    try:
        mac = uuid.getnode()
        # Check if MAC is locally administered (likely random or virtual)
        if (mac >> 40) & 0x02:
            return None
        return ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
    except Exception as e:
        logger.warning(f"Failed to get MAC address: {e}")
        return None


def _get_cpu_info() -> str:
    """
    Get CPU information for the current system.
    
    Returns:
        CPU model string or "UNKNOWN" if unavailable
    """
    try:
        system = platform.system()

        if system == "Windows":
            result = subprocess.check_output([
                "powershell",
                "-Command",
                "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"
            ], stderr=subprocess.DEVNULL)
            return result.decode().strip() or "UNKNOWN"

        elif system == "Linux":
            try:
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
                return "UNKNOWN"
            except FileNotFoundError:
                return "UNKNOWN"

        elif system == "Darwin":
            result = subprocess.check_output([
                "sysctl",
                "-n",
                "machdep.cpu.brand_string"
            ], stderr=subprocess.DEVNULL)
            return result.decode().strip() or "UNKNOWN"

        else:
            return "UNKNOWN"

    except Exception as e:
        logger.warning(f"Failed to get CPU info: {e}")
        return "UNKNOWN"


def _get_system_uuid() -> str:
    """
    Get system UUID for hardware identification.
    
    Returns:
        System UUID string or "UNKNOWN" if unavailable
    """
    try:
        system = platform.system()

        if system == "Windows":
            result = subprocess.check_output([
                "powershell",
                "-Command",
                "Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"
            ], stderr=subprocess.DEVNULL)
            return result.decode().strip() or "UNKNOWN"

        elif system == "Linux":
            try:
                # Prefer machine-id
                with open("/etc/machine-id") as f:
                    return f.read().strip()
            except FileNotFoundError:
                # Fallback to product UUID
                try:
                    with open("/sys/class/dmi/id/product_uuid") as f:
                        return f.read().strip()
                except Exception:
                    return "UNKNOWN"

        elif system == "Darwin":
            result = subprocess.check_output([
                "ioreg", "-rd1", "-c", "IOPlatformExpertDevice"
            ], stderr=subprocess.DEVNULL)
            for line in result.decode().splitlines():
                if "IOPlatformUUID" in line:
                    return line.split('"')[-2]
            return "UNKNOWN"

        else:
            return "UNKNOWN"

    except Exception as e:
        logger.warning(f"Failed to get system UUID: {e}")
        return "UNKNOWN"


def generate_binding_id() -> str:
    """
    Generate a unique hardware binding ID for the current system.
    
    Returns:
        SHA256 hash of system hardware characteristics
    """
    mac = _get_mac_address()
    mac = mac.upper() if mac else "UNKNOWN"

    cpu = _get_cpu_info()
    cpu = cpu.upper() if cpu else "UNKNOWN"

    uuid_val =_get_system_uuid()
    uuid_val = uuid_val.upper() if uuid_val else "UNKNOWN"

    # Combine hardware characteristics
    raw = f"{mac}-{cpu}-{uuid_val}"
    binding_id = hashlib.sha256(raw.encode()).hexdigest()

    logger.debug(f"Generated binding_id: {binding_id}")
    return binding_id


def verify_binding_id(registered_binding_id: str) -> bool:
    """
    Verify if the current system binding ID matches the registered one.
    
    Args:
        registered_binding_id: The binding ID to compare against
        
    Returns:
        True if binding IDs match, False otherwise
    """
    current_binding_id = generate_binding_id().strip().upper()
    registered_binding_id = registered_binding_id.strip().upper()
    
    match = current_binding_id == registered_binding_id
    
    if not match:
        logger.warning(f"Binding ID mismatch - Current: {current_binding_id}, Registered: {registered_binding_id}")
    else:
        logger.info("Binding ID verification successful")
    
    return match 