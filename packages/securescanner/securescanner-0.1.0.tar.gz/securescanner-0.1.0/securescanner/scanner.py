#!/usr/bin/env python3
"""
SecureScanner - Advanced Security Port Scanner and Vulnerability Assessment Tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module provides the core scanning functionality for the SecureScanner package.
It includes port scanning, service detection, vulnerability assessment, and reporting.
"""

import socket
import sys
import threading
from queue import Queue
import time
from datetime import datetime
import ipaddress
import json
import logging
import random
import ssl
from typing import Dict, List, Tuple, Optional
import csv
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security_scan.log'),
        logging.StreamHandler()
    ]
)

class SecurityScanner:
    """
    A comprehensive security scanner that performs port scanning and vulnerability assessment.
    
    This class provides methods for:
    - Port scanning with multi-threading
    - Service banner grabbing
    - OS detection
    - Vulnerability assessment
    - Security report generation
    
    Attributes:
        target (str): The target IP address to scan
        rate_limit (float): Delay between connection attempts for stealth
        output_dir (Path): Directory for saving reports and logs
    """

    # Common vulnerabilities database
    COMMON_VULNERABILITIES = {
        21: ["Anonymous FTP login", "FTP Bounce Attack"],
        22: ["OpenSSH < 7.7 Username Enumeration", "SSH Protocol 1.0"],
        23: ["Telnet Unencrypted", "Default Credentials"],
        80: ["Directory Traversal", "SQL Injection", "XSS"],
        443: ["Heartbleed", "POODLE", "BEAST"],
        3306: ["MySQL Weak Password", "CVE-2016-6662"],
        3389: ["BlueKeep (CVE-2019-0708)", "RDP Session Hijacking"]
    }

    def __init__(self, target: str, output_dir: Optional[str] = None):
        """
        Initialize the SecurityScanner.

        Args:
            target: The target IP address to scan
            output_dir: Optional directory for saving reports and logs
        
        Raises:
            ValueError: If the target IP address is invalid
        """
        if not self._validate_ip(target):
            raise ValueError(f"Invalid IP address: {target}")
        
        self.target = target
        self.open_ports: List[Tuple[int, str, Dict]] = []
        self.scan_time = datetime.now()
        self.os_info = None
        self.rate_limit = 0.1
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_ip(ip: str) -> bool:
        """Validate an IP address."""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def get_service_banner(self, port: int) -> str:
        """
        Attempt to grab the service banner from an open port.
        
        Args:
            port: The port number to grab the banner from
            
        Returns:
            str: The service banner or an error message
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.target, port))
                
                # Try standard connection
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                if not banner and port == 80:
                    # Try HTTP
                    sock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                elif not banner and port == 443:
                    # Try HTTPS
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    with context.wrap_socket(sock) as ssock:
                        ssock.send(b"GET / HTTP/1.1\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                        banner = ssock.recv(1024).decode('utf-8', errors='ignore').strip()
                
                return banner[:100]  # Truncate long banners
        except Exception as e:
            return f"Banner grab failed: {str(e)}"

    def detect_os(self) -> str:
        """
        Attempt to detect the operating system of the target.
        
        Returns:
            str: The detected OS or "Unknown OS"
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                sock.connect((self.target, 80))
                sock.send(b"GET / HTTP/1.1\r\n\r\n")
                response = sock.recv(1024)
                
                if "Windows" in str(response):
                    return "Windows"
                elif "Ubuntu" in str(response):
                    return "Ubuntu Linux"
                elif "Apache" in str(response):
                    return "Linux (Apache)"
                else:
                    return "Unknown OS"
        except:
            return "OS Detection Failed"

    def check_vulnerabilities(self, port: int) -> List[str]:
        """
        Check for common vulnerabilities associated with a port.
        
        Args:
            port: The port number to check
            
        Returns:
            List[str]: List of potential vulnerabilities
        """
        return self.COMMON_VULNERABILITIES.get(port, [])

    def get_service_name(self, port: int) -> str:
        """
        Get the service name for a port number.
        
        Args:
            port: The port number
            
        Returns:
            str: The service name or "unknown"
        """
        try:
            return socket.getservbyport(port)
        except (socket.error, OSError):
            return "unknown"

    def scan_port(self, port: int) -> None:
        """
        Scan a single port and gather security information.
        
        Args:
            port: The port number to scan
        """
        try:
            time.sleep(self.rate_limit)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex((self.target, port))
                
                if result == 0:
                    service_name = self.get_service_name(port)
                    banner = self.get_service_banner(port)
                    vulnerabilities = self.check_vulnerabilities(port)
                    
                    port_info = {
                        'banner': banner,
                        'vulnerabilities': vulnerabilities
                    }
                    
                    self.open_ports.append((port, service_name, port_info))
                    logging.info(f"Found open port {port} ({service_name})")
                    
        except socket.error as e:
            logging.error(f"Error scanning port {port}: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error scanning port {port}: {str(e)}")

    def scan(self, start_port: int = 1, end_port: int = 1024, num_threads: int = 50) -> None:
        """
        Perform the security scan on the target.
        
        Args:
            start_port: First port to scan
            end_port: Last port to scan
            num_threads: Number of concurrent scanning threads
        """
        logging.info(f"Starting security scan on {self.target}")
        logging.info(f"Time started: {self.scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.os_info = self.detect_os()
        logging.info(f"Detected OS: {self.os_info}")

        queue: Queue = Queue()
        threads = []

        # Randomize ports for less predictable scanning
        ports = list(range(start_port, end_port + 1))
        random.shuffle(ports)
        for port in ports:
            queue.put(port)

        def worker():
            while not queue.empty():
                port = queue.get()
                self.scan_port(port)
                queue.task_done()
                remaining = queue.qsize()
                total = end_port - start_port + 1
                progress = ((total - remaining) / total) * 100
                sys.stdout.write(f"\rProgress: {progress:.1f}% - Ports remaining: {remaining}")
                sys.stdout.flush()

        for _ in range(min(num_threads, end_port - start_port + 1)):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            threads.append(t)

        queue.join()
        print("\n\nScan completed!")
        self.generate_report()

    def generate_report(self) -> None:
        """Generate detailed security reports in multiple formats."""
        report = {
            "scan_info": {
                "target": self.target,
                "timestamp": self.scan_time.strftime('%Y-%m-%d %H:%M:%S'),
                "os_detection": self.os_info
            },
            "open_ports": []
        }

        print("\n=== Security Assessment Report ===")
        print(f"\nTarget: {self.target}")
        print(f"OS Detection: {self.os_info}")
        print("\nOpen Ports and Security Findings:")
        
        if self.open_ports:
            self.open_ports.sort()
            for port, service, info in self.open_ports:
                print(f"\n[OPEN] Port {port}")
                print(f"Service: {service}")
                print(f"Banner: {info['banner']}")
                if info['vulnerabilities']:
                    print("Potential Vulnerabilities:")
                    for vuln in info['vulnerabilities']:
                        print(f"  - {vuln}")
                
                report["open_ports"].append({
                    "port": port,
                    "service": service,
                    "banner": info['banner'],
                    "vulnerabilities": info['vulnerabilities']
                })
        else:
            print("\nNo open ports found.")
            
        # Save reports
        json_path = self.output_dir / 'security_report.json'
        csv_path = self.output_dir / 'security_report.csv'
        
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=4)
            
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Port', 'Service', 'Banner', 'Vulnerabilities'])
            for port, service, info in self.open_ports:
                writer.writerow([
                    port,
                    service,
                    info['banner'],
                    '; '.join(info['vulnerabilities'])
                ])
                
        logging.info(f"Security reports generated:\n- {json_path}\n- {csv_path}")
