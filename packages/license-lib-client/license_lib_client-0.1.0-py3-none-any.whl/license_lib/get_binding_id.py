#!/usr/bin/env python3
"""
License Library CLI Tool

This module provides a command-line interface for generating hardware fingerprints
and managing license-related operations.
"""

import argparse
import json
import sys
from typing import Dict, Any
from .binding_id import generate_binding_id, _get_mac_address, _get_cpu_info, _get_system_uuid


def format_hardware_info() -> Dict[str, Any]:
    """
    Get formatted hardware information for display.
    
    Returns:
        Dictionary containing hardware information
    """
    mac = _get_mac_address()
    cpu = _get_cpu_info()
    uuid = _get_system_uuid()
    
    return {
        "mac_address": mac,
        "cpu_info": cpu,
        "system_uuid": uuid,
        "binding_id": generate_binding_id()
    }


def print_hardware_info(verbose: bool = False, json_output: bool = False) -> None:
    """
    Print hardware information in the specified format.
    
    Args:
        verbose: If True, show detailed hardware components
        json_output: If True, output in JSON format
    """
    info = format_hardware_info()
    
    if json_output:
        print(json.dumps(info, indent=2))
        return
    
    if verbose:
        print("Hardware Information:")
        print("=" * 50)
        print(f"MAC Address:     {info['mac_address']}")
        print(f"CPU Info:        {info['cpu_info']}")
        print(f"System UUID:     {info['system_uuid']}")
        print("-" * 50)
        print(f"Binding ID:      {info['binding_id']}")
        print("=" * 50)
    else:
        print(f"Hardware Binding ID: {info['binding_id']}")


def verify_binding_id(binding_id: str) -> None:
    """
    Verify a binding ID against the current system.
    
    Args:
        binding_id: The binding ID to verify
    """
    from .binding_id import verify_binding_id
    
    is_valid = verify_binding_id(binding_id)
    
    if is_valid:
        print("✅ Binding ID verification successful - System matches!")
        sys.exit(0)
    else:
        print("❌ Binding ID verification failed - System mismatch!")
        sys.exit(1)


def main() -> None:
    """
    Main CLI entry point.
    """
    parser = argparse.ArgumentParser(
        description="License Library CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Generate binding ID
  %(prog)s -v                 # Show detailed hardware info
  %(prog)s --json             # Output in JSON format
  %(prog)s verify ABC123      # Verify a binding ID
        """
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed hardware information'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    parser.add_argument(
        'verify',
        nargs='?',
        metavar='BINDING_ID',
        help='Verify a binding ID against the current system'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verify:
            verify_binding_id(args.verify)
        else:
            print_hardware_info(verbose=args.verbose, json_output=args.json)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
