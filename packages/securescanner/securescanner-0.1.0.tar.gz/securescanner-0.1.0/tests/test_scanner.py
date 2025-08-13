"""Test suite for SecureScanner."""
import pytest
from securescanner import SecurityScanner

def test_scanner_initialization():
    """Test scanner initialization with valid and invalid IPs."""
    # Valid IP
    scanner = SecurityScanner("127.0.0.1")
    assert scanner.target == "127.0.0.1"
    
    # Invalid IP
    with pytest.raises(ValueError):
        SecurityScanner("invalid.ip")

def test_validate_ip():
    """Test IP validation function."""
    scanner = SecurityScanner("127.0.0.1")
    assert scanner._validate_ip("127.0.0.1") is True
    assert scanner._validate_ip("192.168.1.1") is True
    assert scanner._validate_ip("256.256.256.256") is False
    assert scanner._validate_ip("invalid.ip") is False

def test_get_service_name():
    """Test service name resolution."""
    scanner = SecurityScanner("127.0.0.1")
    assert scanner.get_service_name(80) == "http"
    assert scanner.get_service_name(443) == "https"
    assert scanner.get_service_name(22) == "ssh"
    
def test_check_vulnerabilities():
    """Test vulnerability checking."""
    scanner = SecurityScanner("127.0.0.1")
    http_vulns = scanner.check_vulnerabilities(80)
    assert isinstance(http_vulns, list)
    assert len(http_vulns) > 0
    assert "SQL Injection" in http_vulns
