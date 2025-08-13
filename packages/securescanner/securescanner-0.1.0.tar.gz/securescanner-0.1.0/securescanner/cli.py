#!/usr/bin/env python3
"""Command-line interface for SecureScanner."""

import argparse
import sys
import logging
from .scanner import SecurityScanner
from .version import __version__

def main():
    """Main entry point for the securescanner command."""
    parser = argparse.ArgumentParser(
        description='SecureScanner - Advanced Security Port Scanner and Vulnerability Assessment Tool',
        epilog='Note: This tool should only be used for authorized security testing.'
    )
    parser.add_argument('target', help='Target IP address')
    parser.add_argument('-s', '--start', type=int, default=1, help='Start port (default: 1)')
    parser.add_argument('-e', '--end', type=int, default=1024, help='End port (default: 1024)')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Number of threads (default: 50)')
    parser.add_argument('--stealth', action='store_true', help='Enable stealth mode (slower but less detectable)')
    parser.add_argument('-o', '--output-dir', help='Directory to save reports and logs')
    parser.add_argument('-v', '--version', action='version', version=f'SecureScanner {__version__}')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level,
                       format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        scanner = SecurityScanner(args.target, args.output_dir)
        if args.stealth:
            scanner.rate_limit = 0.5
            logging.info("Stealth mode enabled - Scan will take longer but be less detectable")
        
        scanner.scan(args.start, args.end, args.threads)
        
    except KeyboardInterrupt:
        logging.warning("\nScan interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"\nAn error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
