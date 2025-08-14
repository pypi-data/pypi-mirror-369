"""
Tests for the CLI module.
"""

import json
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
import pytest
from license_lib.get_binding_id import format_hardware_info, print_hardware_info, verify_binding_id, main


class TestCLI:
    """Test cases for CLI functionality."""

    def test_format_hardware_info(self):
        """Test hardware info formatting."""
        with patch('license_lib.get_binding_id._get_mac_address', return_value="00:11:22:33:44:55"), \
             patch('license_lib.get_binding_id._get_cpu_info', return_value="Intel CPU"), \
             patch('license_lib.get_binding_id._get_system_uuid', return_value="uuid-123"), \
             patch('license_lib.get_binding_id.generate_binding_id', return_value="binding-456"):
            
            info = format_hardware_info()
            
            assert info['mac_address'] == "00:11:22:33:44:55"
            assert info['cpu_info'] == "Intel CPU"
            assert info['system_uuid'] == "uuid-123"
            assert info['binding_id'] == "binding-456"

    def test_print_hardware_info_default(self, capsys):
        """Test default hardware info output."""
        mock_info = {
            'mac_address': "00:11:22:33:44:55",
            'cpu_info': "Intel CPU",
            'system_uuid': "uuid-123",
            'binding_id': "binding-456"
        }
        
        with patch('license_lib.get_binding_id.format_hardware_info', return_value=mock_info):
            print_hardware_info(verbose=False, json_output=False)
            
            captured = capsys.readouterr()
            assert "Hardware Binding ID: binding-456" in captured.out

    def test_print_hardware_info_verbose(self, capsys):
        """Test verbose hardware info output."""
        mock_info = {
            'mac_address': "00:11:22:33:44:55",
            'cpu_info': "Intel CPU",
            'system_uuid': "uuid-123",
            'binding_id': "binding-456"
        }
        
        with patch('license_lib.get_binding_id.format_hardware_info', return_value=mock_info):
            print_hardware_info(verbose=True, json_output=False)
            
            captured = capsys.readouterr()
            assert "Hardware Information:" in captured.out
            assert "MAC Address:     00:11:22:33:44:55" in captured.out
            assert "CPU Info:        Intel CPU" in captured.out
            assert "System UUID:     uuid-123" in captured.out
            assert "Binding ID:      binding-456" in captured.out

    def test_print_hardware_info_json(self, capsys):
        """Test JSON hardware info output."""
        mock_info = {
            'mac_address': "00:11:22:33:44:55",
            'cpu_info': "Intel CPU",
            'system_uuid': "uuid-123",
            'binding_id': "binding-456"
        }
        
        with patch('license_lib.get_binding_id.format_hardware_info', return_value=mock_info):
            print_hardware_info(verbose=False, json_output=True)
            
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output == mock_info

    def test_verify_binding_id_success(self, capsys):
        """Test successful binding ID verification."""
        with patch('license_lib.binding_id.verify_binding_id', return_value=True):
            with pytest.raises(SystemExit) as exc_info:
                verify_binding_id("test-binding-id")
            
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "✅ Binding ID verification successful" in captured.out

    def test_verify_binding_id_failure(self, capsys):
        """Test failed binding ID verification."""
        with patch('license_lib.binding_id.verify_binding_id', return_value=False):
            with pytest.raises(SystemExit) as exc_info:
                verify_binding_id("test-binding-id")
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "❌ Binding ID verification failed" in captured.out

    def test_main_generate_binding_id(self, capsys):
        """Test main function for generating binding ID."""
        mock_info = {
            'mac_address': "00:11:22:33:44:55",
            'cpu_info': "Intel CPU",
            'system_uuid': "uuid-123",
            'binding_id': "binding-456"
        }
        
        with patch('license_lib.get_binding_id.format_hardware_info', return_value=mock_info), \
             patch('sys.argv', ['license-fingerprint']):
            main()
            
            captured = capsys.readouterr()
            assert "Hardware Binding ID: binding-456" in captured.out

    def test_main_verbose(self, capsys):
        """Test main function with verbose flag."""
        mock_info = {
            'mac_address': "00:11:22:33:44:55",
            'cpu_info': "Intel CPU",
            'system_uuid': "uuid-123",
            'binding_id': "binding-456"
        }
        
        with patch('license_lib.get_binding_id.format_hardware_info', return_value=mock_info), \
             patch('sys.argv', ['license-fingerprint', '-v']):
            main()
            
            captured = capsys.readouterr()
            assert "Hardware Information:" in captured.out
            assert "MAC Address:     00:11:22:33:44:55" in captured.out

    def test_main_json(self, capsys):
        """Test main function with JSON flag."""
        mock_info = {
            'mac_address': "00:11:22:33:44:55",
            'cpu_info': "Intel CPU",
            'system_uuid': "uuid-123",
            'binding_id': "binding-456"
        }
        
        with patch('license_lib.get_binding_id.format_hardware_info', return_value=mock_info), \
             patch('sys.argv', ['license-fingerprint', '--json']):
            main()
            
            captured = capsys.readouterr()
            output = json.loads(captured.out)
            assert output == mock_info

    def test_main_verify_success(self, capsys):
        """Test main function for verification success."""
        with patch('license_lib.binding_id.verify_binding_id', return_value=True), \
             patch('sys.argv', ['license-fingerprint', 'test-binding-id']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 0

    def test_main_verify_failure(self, capsys):
        """Test main function for verification failure."""
        with patch('license_lib.binding_id.verify_binding_id', return_value=False), \
             patch('sys.argv', ['license-fingerprint', 'test-binding-id']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1

    def test_main_keyboard_interrupt(self, capsys):
        """Test main function handling KeyboardInterrupt."""
        with patch('license_lib.get_binding_id.format_hardware_info', side_effect=KeyboardInterrupt), \
             patch('sys.argv', ['license-fingerprint']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Operation cancelled by user." in captured.out

    def test_main_exception(self, capsys):
        """Test main function handling general exceptions."""
        with patch('license_lib.get_binding_id.format_hardware_info', side_effect=ValueError("Test error")), \
             patch('sys.argv', ['license-fingerprint']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Error: Test error" in captured.err

    def test_main_help(self, capsys):
        """Test main function help output."""
        with patch('sys.argv', ['license-fingerprint', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "License Library CLI Tool" in captured.out
            assert "Generate binding ID" in captured.out
            assert "Show detailed hardware info" in captured.out
