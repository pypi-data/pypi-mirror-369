"""
SecureScanner - Advanced Security Port Scanner and Vulnerability Assessment Tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A comprehensive security assessment tool that combines port scanning with
vulnerability checking and detailed security reporting.

Basic usage:

    >>> from securescanner import SecurityScanner
    >>> scanner = SecurityScanner('192.168.1.1')
    >>> scanner.scan(start_port=1, end_port=1024)

For command line usage, use the `securescanner` command after installation.
"""

from .scanner import SecurityScanner
from .version import __version__

__all__ = ['SecurityScanner']
