#!/usr/bin/env python3
"""
SpiderFoot Client CLI

Command-line interface for the SpiderFoot API client.
"""

import argparse
import json
import logging
import os
import sys
from typing import Optional

from .client import SpiderFootClient, SpiderFootAPIError


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_client_from_env() -> SpiderFootClient:
    """Create client from environment variables."""
    url = os.getenv('SPIDERFOOT_URL', 'http://localhost:5001')
    username = os.getenv('SPIDERFOOT_USERNAME', 'admin')
    password = os.getenv('SPIDERFOOT_PASSWORD', '')
    
    if not password:
        print("Error: SPIDERFOOT_PASSWORD environment variable is required", file=sys.stderr)
        sys.exit(1)
    
    return SpiderFootClient(url, username, password)


def cmd_ping(args):
    """Test connectivity to SpiderFoot server."""
    client = get_client_from_env()
    try:
        result = client.ping()
        print(json.dumps(result, indent=2))
        return 0 if result.get('status') == 'success' else 1
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_start_scan(args):
    """Start a new scan."""
    client = get_client_from_env()
    try:
        modules = args.modules.split(',') if args.modules else None
        result = client.start_scan(args.target, args.name, modules, args.usecase)
        print(json.dumps(result, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list_scans(args):
    """List all scans."""
    client = get_client_from_env()
    try:
        scans = client.get_scan_list()
        print(json.dumps(scans, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_scan_status(args):
    """Get scan status."""
    client = get_client_from_env()
    try:
        status = client.get_scan_status(args.scan_id)
        print(json.dumps(status, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_stop_scan(args):
    """Stop a running scan."""
    client = get_client_from_env()
    try:
        result = client.stop_scan(args.scan_id)
        print(json.dumps(result, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_delete_scan(args):
    """Delete a scan."""
    client = get_client_from_env()
    try:
        result = client.delete_scan(args.scan_id)
        print(json.dumps(result, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_scan_results(args):
    """Get scan results."""
    client = get_client_from_env()
    try:
        results = client.get_scan_results(args.scan_id, args.event_type)
        print(json.dumps(results, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_scan_summary(args):
    """Get scan summary."""
    client = get_client_from_env()
    try:
        summary = client.get_scan_summary(args.scan_id, args.by)
        print(json.dumps(summary, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_scan_log(args):
    """Get scan log."""
    client = get_client_from_env()
    try:
        log = client.get_scan_log(args.scan_id, args.limit, args.from_rowid)
        print(json.dumps(log, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_export_results(args):
    """Export scan results."""
    client = get_client_from_env()
    try:
        data = client.export_scan_results(args.scan_id, args.format)
        print(json.dumps(data, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_wait_completion(args):
    """Wait for scan completion."""
    client = get_client_from_env()
    try:
        status = client.wait_for_completion(args.scan_id, args.poll_interval, args.timeout)
        print(json.dumps(status, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_modules(args):
    """Get available modules."""
    client = get_client_from_env()
    try:
        modules = client.get_modules()
        print(json.dumps(modules, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_search(args):
    """Search scan results."""
    client = get_client_from_env()
    try:
        results = client.search_results(args.query, args.scan_id)
        print(json.dumps(results, indent=2))
        return 0
    except SpiderFootAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SpiderFoot API Client CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ping command
    ping_parser = subparsers.add_parser('ping', help='Test server connectivity')
    ping_parser.set_defaults(func=cmd_ping)
    
    # Start scan command
    start_parser = subparsers.add_parser('start', help='Start a new scan')
    start_parser.add_argument('target', help='Target to scan (domain, IP, etc.)')
    start_parser.add_argument('name', help='Scan name')
    start_parser.add_argument('--modules', help='Comma-separated list of modules')
    start_parser.add_argument('--usecase', default='all', 
                             choices=['all', 'investigate', 'passive', 'footprint'],
                             help='Scan use case (default: all)')
    start_parser.set_defaults(func=cmd_start_scan)
    
    # List scans command
    list_parser = subparsers.add_parser('list', help='List all scans')
    list_parser.set_defaults(func=cmd_list_scans)
    
    # Scan status command
    status_parser = subparsers.add_parser('status', help='Get scan status')
    status_parser.add_argument('scan_id', help='Scan ID')
    status_parser.set_defaults(func=cmd_scan_status)
    
    # Stop scan command
    stop_parser = subparsers.add_parser('stop', help='Stop a running scan')
    stop_parser.add_argument('scan_id', help='Scan ID')
    stop_parser.set_defaults(func=cmd_stop_scan)
    
    # Delete scan command
    delete_parser = subparsers.add_parser('delete', help='Delete a scan')
    delete_parser.add_argument('scan_id', help='Scan ID')
    delete_parser.set_defaults(func=cmd_delete_scan)
    
    # Scan results command
    results_parser = subparsers.add_parser('results', help='Get scan results')
    results_parser.add_argument('scan_id', help='Scan ID')
    results_parser.add_argument('--event-type', help='Filter by event type')
    results_parser.set_defaults(func=cmd_scan_results)
    
    # Scan summary command
    summary_parser = subparsers.add_parser('summary', help='Get scan summary')
    summary_parser.add_argument('scan_id', help='Scan ID')
    summary_parser.add_argument('--by', default='module', help='Summary type (default: module)')
    summary_parser.set_defaults(func=cmd_scan_summary)
    
    # Scan log command
    log_parser = subparsers.add_parser('log', help='Get scan log')
    log_parser.add_argument('scan_id', help='Scan ID')
    log_parser.add_argument('--limit', type=int, help='Maximum number of entries')
    log_parser.add_argument('--from-rowid', type=int, help='Start from row ID')
    log_parser.set_defaults(func=cmd_scan_log)
    
    # Export results command
    export_parser = subparsers.add_parser('export', help='Export scan results')
    export_parser.add_argument('scan_id', help='Scan ID')
    export_parser.add_argument('--format', default='json', 
                              choices=['json', 'csv', 'xlsx'],
                              help='Export format (default: json)')
    export_parser.set_defaults(func=cmd_export_results)
    
    # Wait for completion command
    wait_parser = subparsers.add_parser('wait', help='Wait for scan completion')
    wait_parser.add_argument('scan_id', help='Scan ID')
    wait_parser.add_argument('--poll-interval', type=int, default=5,
                            help='Seconds between status checks (default: 5)')
    wait_parser.add_argument('--timeout', type=int, help='Maximum seconds to wait')
    wait_parser.set_defaults(func=cmd_wait_completion)
    
    # Modules command
    modules_parser = subparsers.add_parser('modules', help='Get available modules')
    modules_parser.set_defaults(func=cmd_modules)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search scan results')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--scan-id', help='Limit search to specific scan')
    search_parser.set_defaults(func=cmd_search)
    
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    setup_logging(args.debug)
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())