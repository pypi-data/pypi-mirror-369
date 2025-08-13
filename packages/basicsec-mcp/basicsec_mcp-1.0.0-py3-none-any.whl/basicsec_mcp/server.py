#!/usr/bin/env python3
"""
BasicSec MCP Server

An MCP server that provides comprehensive email security scanning capabilities
using the basicsec library for DNS and email security checks.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from mcp.server import FastMCP
from basicsec import BasicSecurityScanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("BasicSec Security Scanner")


@mcp.tool()
def passive_scan(
    domain: str,
    dns_timeout: float = 5.0,
    dns_hostnames: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform a passive email security scan that only checks DNS records
    without making SMTP connections.
    
    Args:
        domain: Domain name to scan
        dns_timeout: DNS lookup timeout in seconds (default: 5.0)
        dns_hostnames: Optional list of DNS hostnames to use (not implemented yet)
    
    Returns:
        Dictionary containing scan results
    """
    try:
        logger.info(f"Starting passive scan for domain: {domain}")
        
        scanner = BasicSecurityScanner(timeout=dns_timeout)
        result = scanner.passive_scan(domain)
        
        # Add timestamp for MCP compatibility
        result['scan_timestamp'] = str(asyncio.get_event_loop().time())
        
        logger.info(f"Passive scan completed for domain: {domain}")
        return result
        
    except Exception as e:
        logger.error(f"Error during passive scan of {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain,
            'scan_type': 'passive'
        }


@mcp.tool()
def active_scan(
    domain: str,
    dns_timeout: float = 5.0,
    smtp_timeout: float = 3.0,
    smtp_ports: Optional[List[int]] = None,
    dns_hostnames: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform an active email security scan that includes both DNS checks
    and SMTP server connectivity tests.
    
    Args:
        domain: Domain name to scan
        dns_timeout: DNS lookup timeout in seconds (default: 5.0)
        smtp_timeout: SMTP connection timeout in seconds (default: 3.0)
        smtp_ports: List of SMTP ports to test (default: [25, 465, 587])
        dns_hostnames: Optional list of DNS hostnames to use (not implemented yet)
    
    Returns:
        Dictionary containing comprehensive scan results
    """
    try:
        logger.info(f"Starting active scan for domain: {domain}")
        
        if smtp_ports is None:
            smtp_ports = [25, 465, 587]
        
        scanner = BasicSecurityScanner(timeout=dns_timeout)
        result = scanner.active_scan(domain, smtp_timeout=smtp_timeout, smtp_ports=smtp_ports)
        
        # Add timestamp for MCP compatibility
        result['scan_timestamp'] = str(asyncio.get_event_loop().time())
        
        logger.info(f"Active scan completed for domain: {domain}")
        return result
        
    except Exception as e:
        logger.error(f"Error during active scan of {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain,
            'scan_type': 'active'
        }


@mcp.tool()
def scan_multiple_domains(
    domains: List[str],
    scan_type: str = "active",
    dns_timeout: float = 3.0,
    smtp_timeout: float = 2.0,
    smtp_ports: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Scan multiple domains with specified scan type.
    Optimized for faster execution to avoid MCP timeouts.
    
    Args:
        domains: List of domain names to scan (recommended: max 5 domains)
        scan_type: Type of scan - "passive" or "active" (default: "active")
        dns_timeout: DNS lookup timeout in seconds (default: 3.0, reduced for speed)
        smtp_timeout: SMTP connection timeout in seconds (default: 2.0, reduced for speed)
        smtp_ports: List of SMTP ports to test (default: [25] for speed)
    
    Returns:
        Dictionary with results for each domain
    """
    # Limit number of domains to prevent timeouts
    if len(domains) > 10:
        logger.warning(f"Limiting scan to first 10 domains (requested: {len(domains)})")
        domains = domains[:10]
    
    # Use faster defaults for multiple domain scans
    if smtp_ports is None:
        smtp_ports = [25]  # Only test port 25 for speed
    
    try:
        scanner = BasicSecurityScanner(timeout=dns_timeout)
        result = scanner.scan_multiple_domains(domains, scan_type)
        
        # Add performance optimization flag
        result['performance_optimized'] = True
        result['note'] = 'Results optimized for speed - use individual scans for detailed analysis'
        
        return result
        
    except Exception as e:
        logger.error(f"Error scanning multiple domains: {str(e)}")
        return {
            'error': str(e),
            'domains': domains,
            'scan_type': scan_type
        }


@mcp.tool()
def quick_domain_check(
    domains: List[str],
    check_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform very quick checks on multiple domains to avoid MCP timeouts.
    Optimized for speed with minimal DNS lookups.
    
    Args:
        domains: List of domain names to check (up to 20 domains)
        check_types: Types of checks to perform: ["live", "mx", "spf", "dmarc", "dnssec"]
                    Default: ["live", "mx", "spf", "dmarc"]
    
    Returns:
        Dictionary with quick check results for each domain
    """
    if check_types is None:
        check_types = ["live", "mx", "spf", "dmarc", "dnssec"]
    
    # Hard limit to prevent timeouts
    if len(domains) > 20:
        logger.warning(f"Limiting quick check to first 20 domains (requested: {len(domains)})")
        domains = domains[:20]
    
    try:
        scanner = BasicSecurityScanner(timeout=2.0)  # Very short timeout
        result = scanner.quick_domain_check(domains, check_types)
        
        result['note'] = 'Quick checks optimized for speed - limited detail'
        
        return result
        
    except Exception as e:
        logger.error(f"Error in quick domain check: {str(e)}")
        return {
            'error': str(e),
            'domains': domains,
            'check_types': check_types
        }


@mcp.tool()
def get_mx_records(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Get MX records for a domain.
    
    Args:
        domain: Domain name to query
        timeout: DNS timeout in seconds
    
    Returns:
        Dictionary containing MX records
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        mx_records = scanner.get_mx_records(domain)
        
        return {
            'domain': domain,
            'mx_records': mx_records,
            'mx_count': len(mx_records),
            'has_mx_records': len(mx_records) > 0
        }
        
    except Exception as e:
        logger.error(f"Error getting MX records for {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain
        }


@mcp.tool()
def get_spf_record(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Get and validate SPF record for a domain.
    
    Args:
        domain: Domain name to query
        timeout: DNS timeout in seconds
    
    Returns:
        Dictionary containing SPF record and validation results
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        spf_record = scanner.get_spf_record(domain)
        
        if spf_record:
            validation = scanner.validate_spf_record(spf_record)
            return {
                'domain': domain,
                'spf_record': spf_record,
                'has_spf_record': True,
                'spf_valid': validation['valid'],
                'spf_policy': validation.get('policy'),
                'spf_mechanisms': validation.get('mechanisms', []),
                'spf_errors': validation.get('errors', [])
            }
        else:
            return {
                'domain': domain,
                'spf_record': None,
                'has_spf_record': False,
                'spf_valid': False,
                'spf_errors': ['No SPF record found']
            }
            
    except Exception as e:
        logger.error(f"Error getting SPF record for {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain
        }


@mcp.tool()
def get_dmarc_record(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Get and validate DMARC record for a domain.
    
    Args:
        domain: Domain name to query
        timeout: DNS timeout in seconds
    
    Returns:
        Dictionary containing DMARC record and validation results
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        dmarc_record = scanner.get_dmarc_record(domain)
        
        if dmarc_record:
            validation = scanner.validate_dmarc_record(dmarc_record)
            return {
                'domain': domain,
                'dmarc_record': dmarc_record,
                'has_dmarc_record': True,
                'dmarc_valid': validation['valid'],
                'dmarc_policy': validation.get('policy'),
                'dmarc_subdomain_policy': validation.get('subdomain_policy'),
                'dmarc_percentage': validation.get('percentage'),
                'dmarc_errors': validation.get('errors', [])
            }
        else:
            return {
                'domain': domain,
                'dmarc_record': None,
                'has_dmarc_record': False,
                'dmarc_valid': False,
                'dmarc_errors': ['No DMARC record found']
            }
            
    except Exception as e:
        logger.error(f"Error getting DMARC record for {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain
        }


@mcp.tool()
def check_dnssec_status(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Check DNSSEC status for a domain.
    
    Args:
        domain: Domain name to query
        timeout: DNS timeout in seconds
    
    Returns:
        Dictionary containing DNSSEC status information
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        result = scanner.get_dnssec_status(domain)
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking DNSSEC status for {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain
        }


@mcp.tool()
def validate_dnssec_chain(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Validate DNSSEC chain of trust for a domain.
    
    Args:
        domain: Domain name to validate
        timeout: DNS timeout in seconds
    
    Returns:
        Dictionary containing chain validation results
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        result = scanner.validate_dnssec_chain(domain)
        
        return result
        
    except Exception as e:
        logger.error(f"Error validating DNSSEC chain for {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain
        }


@mcp.tool()
def test_smtp_connection(
    hostname: str,
    port: int = 25,
    timeout: float = 3.0
) -> Dict[str, Any]:
    """
    Test SMTP connection and STARTTLS support for a specific hostname.
    
    Args:
        hostname: SMTP server hostname
        port: SMTP port (default: 25)
        timeout: Connection timeout in seconds
    
    Returns:
        Dictionary containing connection test results
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        result = scanner.test_smtp_connection(hostname, port, timeout)
        
        return result
        
    except Exception as e:
        logger.error(f"Error testing SMTP connection to {hostname}:{port}: {str(e)}")
        return {
            'error': str(e),
            'hostname': hostname,
            'port': port
        }


@mcp.tool()
def analyze_dnssec_security(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Perform comprehensive DNSSEC security analysis to detect issues like
    deprecated digest algorithms, weak cryptographic algorithms, and other
    security concerns.
    
    Args:
        domain: Domain name to analyze
        timeout: DNS timeout in seconds
    
    Returns:
        Dictionary containing comprehensive DNSSEC security analysis with:
        - security_score: Overall security assessment
        - security_issues: Critical security problems found
        - warnings: Security warnings and concerns
        - recommendations: Suggestions for improvement
        - algorithm_analysis: Details about algorithms used
        - digest_analysis: Analysis of digest algorithms
        - key_analysis: Key management analysis
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        result = scanner.analyze_dnssec_security(domain)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing DNSSEC security for {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain,
            'security_score': 'error',
            'security_issues': [f"Analysis failed: {str(e)}"]
        }


@mcp.tool()
def analyze_dnssec_upstream_security(
    domain: str, 
    check_upstream: bool = True,
    timeout: float = 5.0
) -> Dict[str, Any]:
    """
    Perform comprehensive DNSSEC security analysis for a domain and all its
    upstream zones (parent zones up to root). This checks the entire DNSSEC
    chain for security issues like deprecated algorithms.
    
    For example, checking example.com will analyze:
    - example.com zone
    - com zone (.com top-level domain)
    - root zone
    
    Args:
        domain: Domain name to analyze
        check_upstream: Whether to analyze parent zones (default: True)
        timeout: DNS timeout in seconds
    
    Returns:
        Dictionary containing comprehensive upstream DNSSEC chain analysis with:
        - upstream_analysis: Security analysis for each zone in the chain
        - total_zones_analyzed: Number of zones checked
        - zones_with_issues: List of zones with security issues
        - zones_with_warnings: List of zones with warnings
        - overall_security_score: Overall assessment of the entire chain
        - chain_security_issues: All security issues found in the chain
        - chain_security_warnings: All warnings found in the chain
        - chain_recommendations: Recommendations for the entire chain
    """
    try:
        scanner = BasicSecurityScanner(timeout=timeout)
        result = scanner.analyze_dnssec_upstream_security(domain, check_upstream)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing upstream DNSSEC security for {domain}: {str(e)}")
        return {
            'error': str(e),
            'domain': domain,
            'overall_security_score': 'error',
            'chain_security_issues': [f"Upstream analysis failed: {str(e)}"]
        }


def main():
    """Main entry point for the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
