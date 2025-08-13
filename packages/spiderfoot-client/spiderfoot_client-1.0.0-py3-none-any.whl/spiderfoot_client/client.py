"""
SpiderFoot API Client

A client for interacting with SpiderFoot API v4.0 using HTTP Digest Authentication.
Based on the implementation patterns from sfcli.py.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

import requests
from requests.auth import HTTPDigestAuth


logger = logging.getLogger(__name__)


class SpiderFootAPIError(Exception):
    """Exception raised for SpiderFoot API errors."""
    pass


class SpiderFootClient:
    """SpiderFoot API client with HTTP Digest authentication."""
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize SpiderFoot client.
        
        Args:
            base_url: Base URL of SpiderFoot instance (e.g., http://localhost:5001)
            username: Username for HTTP digest auth
            password: Password for HTTP digest auth
        """
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPDigestAuth(username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        # Set default headers like sfcli does
        self.session.headers.update({
            'User-Agent': 'SpiderFoot-Client/1.0',
            'Accept': 'application/json'
        })
        
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to SpiderFoot API.
        
        Args:
            endpoint: API endpoint (without leading slash)
            method: HTTP method
            data: Request data for POST requests
            
        Returns:
            JSON response data
            
        Raises:
            SpiderFootAPIError: If request fails
        """
        url = urljoin(f"{self.base_url}/", endpoint)
        
        try:
            if method.upper() == 'POST':
                logger.debug(f"POST {url} with data: {data}")
                response = self.session.post(url, data=data)
            else:
                logger.debug(f"GET {url} with params: {data}")
                response = self.session.get(url, params=data)
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            # Handle empty responses
            if not response.content:
                return {}
                
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Request to {url} failed: {e}")
            logger.error(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
            logger.error(f"Response text: {getattr(e.response, 'text', 'N/A')}")
            raise SpiderFootAPIError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response from {url}: {e}")
            logger.error(f"Response text: {response.text}")
            raise SpiderFootAPIError(f"Invalid JSON response: {e}")
    
    def start_scan(self, target: str, scan_name: str, modules: Optional[List[str]] = None, 
                   use_case: str = "all") -> Dict[str, Any]:
        """
        Start a new scan.
        
        Args:
            target: Target to scan (domain, IP, etc.)
            scan_name: Name for the scan
            modules: List of modules to use (None for default usecase modules)
            use_case: Use case type ("all", "investigate", "passive", "footprint")
            
        Returns:
            Scan information including scan ID
        """
        data = {
            'scanname': scan_name,
            'scantarget': target,
            'usecase': use_case,
            'modulelist': '',  # Always include modulelist, even if empty
            'typelist': ''     # Always include typelist, even if empty
        }
        
        if modules:
            data['modulelist'] = ','.join(modules)
        elif use_case == "passive":
            # Provide some default passive modules if none specified
            default_passive = ["sfp_dnscommonsrv", "sfp_dnsresolve"]
            data['modulelist'] = ','.join(default_passive)
            
        result = self._make_request('startscan', 'POST', data)
        logger.info(f"Started scan '{scan_name}' for target '{target}'")
        
        # Handle SpiderFoot API response format: ['SUCCESS', 'scan_id'] or ['ERROR', 'message']
        if isinstance(result, list) and len(result) >= 2:
            if result[0] == 'SUCCESS':
                return {'id': result[1], 'status': 'success'}
            elif result[0] == 'ERROR':
                raise SpiderFootAPIError(f"Scan failed: {result[1]}")
        
        return result
    
    def get_scan_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all scans.
        
        Returns:
            List of scan information dictionaries
        """
        result = self._make_request('scanlist')
        # Handle both list and dict responses
        if isinstance(result, list):
            return result
        return result.get('scans', [])
    
    def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """
        Get status of a specific scan.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            Scan status information
        """
        scans = self.get_scan_list()
        for scan in scans:
            # Handle SpiderFoot scan list format: [scan_id, name, target, created, started, completed, status, ...]
            if isinstance(scan, list) and len(scan) >= 7:
                if scan[0] == scan_id:
                    return {
                        'id': scan[0],
                        'name': scan[1],
                        'target': scan[2], 
                        'created': scan[3],
                        'started': scan[4],
                        'completed': scan[5],
                        'status': scan[6]
                    }
            elif isinstance(scan, dict) and scan.get('id') == scan_id:
                return scan
        raise SpiderFootAPIError(f"Scan {scan_id} not found")
    
    def stop_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Stop a running scan.
        
        Args:
            scan_id: Scan ID to stop
            
        Returns:
            API response
        """
        data = {'id': scan_id}
        result = self._make_request('stopscan', 'POST', data)
        logger.info(f"Stopped scan {scan_id}")
        return result
    
    def delete_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Delete a scan.
        
        Args:
            scan_id: Scan ID to delete
            
        Returns:
            API response
        """
        data = {'id': scan_id}
        result = self._make_request('scandelete', 'POST', data)
        logger.info(f"Deleted scan {scan_id}")
        return result
    
    def get_scan_results(self, scan_id: str, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get results from a scan.
        
        Args:
            scan_id: Scan ID
            event_type: Optional event type filter
            
        Returns:
            List of scan result events
        """
        params = {'id': scan_id}
        if event_type:
            params['eventType'] = event_type
            
        result = self._make_request('scaneventresults', data=params)
        # Handle both list and dict response formats
        if isinstance(result, list):
            return result
        return result.get('results', [])
    
    def get_scan_summary(self, scan_id: str, by: str = "module") -> Dict[str, Any]:
        """
        Get scan summary.
        
        Args:
            scan_id: Scan ID
            by: Summary filter type (default: "module")
            
        Returns:
            Scan summary data
        """
        params = {'id': scan_id, 'by': by}
        return self._make_request('scansummary', data=params)
    
    def get_scan_log(self, scan_id: str, limit: Optional[int] = None, 
                     from_rowid: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get scan log entries.
        
        Args:
            scan_id: Scan ID
            limit: Maximum number of entries to return
            from_rowid: Start from specific row ID for pagination
            
        Returns:
            List of log entries
        """
        params = {'id': scan_id}
        if limit:
            params['limit'] = str(limit)
        if from_rowid:
            params['rowId'] = str(from_rowid)
            
        result = self._make_request('scanlog', data=params)
        # Handle both list and dict response formats
        if isinstance(result, list):
            return result
        return result.get('log', [])
    
    def export_scan_results(self, scan_id: str, export_format: str = 'json') -> Dict[str, Any]:
        """
        Export scan results.
        
        Args:
            scan_id: Scan ID
            export_format: Export format (json, csv, xlsx)
            
        Returns:
            Exported data
        """
        if export_format.lower() == 'json':
            # Use JSON multi export endpoint
            params = {'ids': scan_id}  # Use 'ids' parameter for JSON export
            return self._make_request('scanexportjsonmulti', data=params)
        elif export_format.lower() in ['csv', 'xlsx', 'excel']:
            # Use event result export for CSV/Excel
            filetype = 'xlsx/excel' if export_format.lower() in ['xlsx', 'excel'] else 'csv'
            params = {
                'id': scan_id,
                'type': '',  # All event types
                'filetype': filetype,
                'dialect': 'excel'
            }
            return self._make_request('scaneventresultexport', data=params)
        else:
            raise SpiderFootAPIError(f"Unsupported export format: {export_format}")
    
    def wait_for_completion(self, scan_id: str, poll_interval: int = 5, 
                           timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Wait for scan to complete.
        
        Args:
            scan_id: Scan ID to monitor
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait (None for no timeout)
            
        Returns:
            Final scan status
            
        Raises:
            SpiderFootAPIError: If scan fails or timeout occurs
        """
        start_time = time.time()
        
        while True:
            status = self.get_scan_status(scan_id)
            scan_status = status.get('status', '').lower()
            
            if scan_status == 'finished':
                logger.info(f"Scan {scan_id} completed successfully")
                return status
            elif scan_status in ['failed', 'aborted']:
                raise SpiderFootAPIError(f"Scan {scan_id} {scan_status}")
            elif scan_status in ['running', 'started', 'starting']:
                if timeout and (time.time() - start_time) > timeout:
                    raise SpiderFootAPIError(f"Scan {scan_id} timed out after {timeout} seconds")
                    
                logger.debug(f"Scan {scan_id} still running, waiting...")
                time.sleep(poll_interval)
            else:
                logger.warning(f"Unknown scan status: {scan_status}")
                time.sleep(poll_interval)
    
    def get_modules(self) -> Dict[str, Any]:
        """
        Get available modules.
        
        Returns:
            Module information
        """
        return self._make_request('modules')
    
    def search_results(self, query: str, scan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search across scan results.
        
        Args:
            query: Search query
            scan_id: Optional scan ID to limit search
            
        Returns:
            Search results
        """
        params = {'value': query}
        if scan_id:
            params['id'] = scan_id
            
        result = self._make_request('search', data=params)
        return result.get('results', [])
    
    def ping(self) -> Dict[str, Any]:
        """
        Test connectivity to SpiderFoot server.
        
        Returns:
            Server ping response with status and version
        """
        result = self._make_request('ping')
        
        # Handle SpiderFoot ping response format: ['SUCCESS', 'version'] or ['ERROR', 'message']
        if isinstance(result, list) and len(result) >= 2:
            if result[0] == 'SUCCESS':
                return {
                    'status': 'success',
                    'server_version': result[1],
                    'message': 'Server responding'
                }
            elif result[0] == 'ERROR':
                return {
                    'status': 'error',
                    'message': result[1]
                }
        
        # Fallback for unexpected response format
        return {
            'status': 'unknown',
            'response': result,
            'message': 'Unexpected response format'
        }