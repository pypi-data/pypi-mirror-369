#!/usr/bin/env python3
"""
SpiderFoot MCP Server

A Model Context Protocol server that provides SpiderFoot scanning capabilities.
Supports starting scans, monitoring progress, and retrieving results.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp.server import FastMCP
from spiderfoot_client import SpiderFootClient, SpiderFootAPIError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("SpiderFoot Scanner")

# Global client instance
spiderfoot_client: Optional[SpiderFootClient] = None

# Scan tracking
active_scans: Dict[str, Dict[str, Any]] = {}


def get_client() -> SpiderFootClient:
    """Get or create SpiderFoot client instance."""
    global spiderfoot_client
    
    if spiderfoot_client is None:
        url = os.getenv('SPIDERFOOT_URL', 'http://localhost:5001')
        username = os.getenv('SPIDERFOOT_USERNAME', 'admin')
        password = os.getenv('SPIDERFOOT_PASSWORD', '')
        
        if not password:
            raise ValueError("SPIDERFOOT_PASSWORD environment variable is required")
            
        spiderfoot_client = SpiderFootClient(url, username, password)
        # logger.info(f"Initialized SpiderFoot client for {url}")
    
    return spiderfoot_client


@mcp.tool()
def start_scan(target: str, scan_name: str, modules: Optional[List[str]] = None, 
               use_case: str = "all") -> Dict[str, Any]:
    """
    Start a new SpiderFoot scan.
    
    Args:
        target: Target to scan (domain, IP address, etc.)
        scan_name: Unique name for the scan
        modules: List of specific modules to use (optional, uses all if not specified)
        use_case: Scan use case - "all", "investigate", "passive", or "footprint"
    
    Returns:
        Dictionary with scan information including scan_id
    """
    try:
        client = get_client()
        result = client.start_scan(target, scan_name, modules, use_case)
        
        # Extract scan ID from result
        scan_id = result.get('id')
        if not scan_id:
            raise SpiderFootAPIError("No scan ID returned from API")
        
        # Track the scan
        active_scans[scan_id] = {
            'target': target,
            'scan_name': scan_name,
            'modules': modules or [],
            'use_case': use_case,
            'status': 'started',
            'created_at': result.get('created', '')
        }
        
        return {
            'success': True,
            'scan_id': scan_id,
            'message': f"Started scan '{scan_name}' for target '{target}'",
            'details': result
        }
        
    except Exception as e:
        logger.error(f"Failed to start scan: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to start scan '{scan_name}'"
        }


@mcp.tool()
def get_scan_status(scan_id: str) -> Dict[str, Any]:
    """
    Get the current status of a scan.
    
    Args:
        scan_id: The scan ID to check
        
    Returns:
        Dictionary with scan status information
    """
    try:
        client = get_client()
        status = client.get_scan_status(scan_id)
        
        # Update tracked scan info
        if scan_id in active_scans:
            active_scans[scan_id]['status'] = status.get('status', 'unknown')
        
        return {
            'success': True,
            'scan_id': scan_id,
            'status': status
        }
        
    except Exception as e:
        logger.error(f"Failed to get scan status: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to get status for scan {scan_id}"
        }


@mcp.tool()
def list_scans() -> Dict[str, Any]:
    """
    List all scans on the SpiderFoot server.
    
    Returns:
        Dictionary with list of all scans
    """
    try:
        client = get_client()
        scans = client.get_scan_list()
        
        return {
            'success': True,
            'scans': scans,
            'count': len(scans)
        }
        
    except Exception as e:
        logger.error(f"Failed to list scans: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve scan list"
        }


@mcp.tool()
def stop_scan(scan_id: str) -> Dict[str, Any]:
    """
    Stop a running scan.
    
    Args:
        scan_id: The scan ID to stop
        
    Returns:
        Dictionary with operation result
    """
    try:
        client = get_client()
        result = client.stop_scan(scan_id)
        
        # Update tracked scan status
        if scan_id in active_scans:
            active_scans[scan_id]['status'] = 'stopped'
        
        return {
            'success': True,
            'scan_id': scan_id,
            'message': f"Stopped scan {scan_id}",
            'details': result
        }
        
    except Exception as e:
        logger.error(f"Failed to stop scan: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to stop scan {scan_id}"
        }


@mcp.tool()
def delete_scan(scan_id: str) -> Dict[str, Any]:
    """
    Delete a scan and all its data.
    
    Args:
        scan_id: The scan ID to delete
        
    Returns:
        Dictionary with operation result
    """
    try:
        client = get_client()
        result = client.delete_scan(scan_id)
        
        # Remove from tracked scans
        if scan_id in active_scans:
            del active_scans[scan_id]
        
        return {
            'success': True,
            'scan_id': scan_id,
            'message': f"Deleted scan {scan_id}",
            'details': result
        }
        
    except Exception as e:
        logger.error(f"Failed to delete scan: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to delete scan {scan_id}"
        }


@mcp.tool()
def get_scan_results(scan_id: str, event_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get results from a completed or running scan.
    
    Args:
        scan_id: The scan ID to get results for
        event_type: Optional filter for specific event types
        
    Returns:
        Dictionary with scan results
    """
    try:
        client = get_client()
        results = client.get_scan_results(scan_id, event_type)
        
        return {
            'success': True,
            'scan_id': scan_id,
            'results': results,
            'count': len(results),
            'event_type_filter': event_type
        }
        
    except Exception as e:
        logger.error(f"Failed to get scan results: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to get results for scan {scan_id}"
        }


@mcp.tool()
def get_scan_summary(scan_id: str, by: str = "module") -> Dict[str, Any]:
    """
    Get a summary of scan results.
    
    Args:
        scan_id: The scan ID to get summary for
        by: Summary filter type ("module", "type", etc.)
        
    Returns:
        Dictionary with scan summary
    """
    try:
        client = get_client()
        summary = client.get_scan_summary(scan_id, by)
        
        return {
            'success': True,
            'scan_id': scan_id,
            'summary': summary
        }
        
    except Exception as e:
        logger.error(f"Failed to get scan summary: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to get summary for scan {scan_id}"
        }


@mcp.tool()
def wait_for_scan_completion(scan_id: str, poll_interval: int = 5, 
                           timeout: Optional[int] = None) -> Dict[str, Any]:
    """
    Wait for a scan to complete and return final status.
    
    Args:
        scan_id: The scan ID to monitor
        poll_interval: Seconds between status checks (default: 5)
        timeout: Maximum seconds to wait (default: no timeout)
        
    Returns:
        Dictionary with final scan status
    """
    try:
        client = get_client()
        final_status = client.wait_for_completion(scan_id, poll_interval, timeout)
        
        # Update tracked scan status
        if scan_id in active_scans:
            active_scans[scan_id]['status'] = final_status.get('status', 'unknown')
        
        return {
            'success': True,
            'scan_id': scan_id,
            'message': f"Scan {scan_id} completed",
            'final_status': final_status
        }
        
    except Exception as e:
        logger.error(f"Failed to wait for scan completion: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to wait for scan {scan_id} completion"
        }


@mcp.tool()
def export_scan_results(scan_id: str, export_format: str = 'json') -> Dict[str, Any]:
    """
    Export scan results in specified format.
    
    Args:
        scan_id: The scan ID to export
        export_format: Export format (json, csv, etc.)
        
    Returns:
        Dictionary with exported data
    """
    try:
        client = get_client()
        exported_data = client.export_scan_results(scan_id, export_format)
        
        return {
            'success': True,
            'scan_id': scan_id,
            'format': export_format,
            'data': exported_data
        }
        
    except Exception as e:
        logger.error(f"Failed to export scan results: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to export results for scan {scan_id}"
        }


@mcp.tool()
def get_available_modules() -> Dict[str, Any]:
    """
    Get list of available SpiderFoot modules.
    
    Returns:
        Dictionary with available modules
    """
    try:
        client = get_client()
        modules = client.get_modules()
        
        return {
            'success': True,
            'modules': modules
        }
        
    except Exception as e:
        logger.error(f"Failed to get modules: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': "Failed to retrieve available modules"
        }


@mcp.tool()
def search_scan_results(query: str, scan_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Search across scan results.
    
    Args:
        query: Search query string
        scan_id: Optional scan ID to limit search to specific scan
        
    Returns:
        Dictionary with search results
    """
    try:
        client = get_client()
        results = client.search_results(query, scan_id)
        
        return {
            'success': True,
            'query': query,
            'scan_id': scan_id,
            'results': results,
            'count': len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to search results: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to search for '{query}'"
        }


@mcp.tool()
def get_scan_log(scan_id: str, limit: Optional[int] = None, 
                 from_rowid: Optional[int] = None) -> Dict[str, Any]:
    """
    Get log entries for a scan.
    
    Args:
        scan_id: The scan ID to get logs for
        limit: Maximum number of log entries to return
        from_rowid: Start from specific row ID for pagination
        
    Returns:
        Dictionary with log entries
    """
    try:
        client = get_client()
        log_entries = client.get_scan_log(scan_id, limit, from_rowid)
        
        return {
            'success': True,
            'scan_id': scan_id,
            'log_entries': log_entries,
            'count': len(log_entries),
            'limit': limit,
            'from_rowid': from_rowid
        }
        
    except Exception as e:
        logger.error(f"Failed to get scan log: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to get log for scan {scan_id}"
        }


@mcp.tool()
def get_active_scans_summary() -> Dict[str, Any]:
    """
    Get summary of scans being tracked by this MCP server.
    
    Returns:
        Dictionary with active scans summary
    """
    return {
        'success': True,
        'active_scans': active_scans,
        'count': len(active_scans)
    }


@mcp.tool()
def ping() -> Dict[str, Any]:
    """
    Test connectivity to the SpiderFoot server.
    
    Returns:
        Dictionary with server connectivity status and version information
    """
    try:
        client = get_client()
        ping_result = client.ping()
        
        return {
            'success': True,
            'status': ping_result.get('status'),
            'server_version': ping_result.get('server_version'),
            'message': ping_result.get('message', 'Server ping successful'),
            'server_url': client.base_url
        }
        
    except Exception as e:
        logger.error(f"Failed to ping server: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': "Failed to ping SpiderFoot server"
        }


def main():
    """Main entry point for the MCP server."""
    import sys
    
    # Validate environment variables
    required_env_vars = ['SPIDERFOOT_URL', 'SPIDERFOOT_USERNAME', 'SPIDERFOOT_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables or create a .env file")
        sys.exit(1)
    
    # Test connection
    try:
        client = get_client()
        scans = client.get_scan_list()

    except Exception as e:
        logger.error(f"Failed to connect to SpiderFoot: {e}")
        sys.exit(1)
    
    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
