#!/usr/bin/env python3
"""
Test script demonstrating TLS/HTTPS support in the modernized HiLink API
"""
import logging
import sys
import os

# Add parent directory to path to import HiLinkAPI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HiLinkAPI import HiLinkAPI, HiLinkException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_http_connection():
    """Test standard HTTP connection (default)"""
    print("\n" + "="*60)
    print("Testing HTTP Connection (Default)")
    print("="*60)
    
    # Create API instance with default HTTP
    api = HiLinkAPI(
        modem_name="TestModem_HTTP",
        host="192.168.8.1",
        username="admin",
        password="admin",
        logger=logger
    )
    
    print(f"Protocol: {api.protocol}")
    print(f"Base URL: {api.base_url}")
    print(f"Use TLS: {api.use_tls}")
    print(f"Verify TLS: {api.verify_tls}")
    
    try:
        # Initialize API
        if api.initialize():
            print(f"✓ Successfully connected via HTTP")
            print(f"  WebUI version: {api.webui_version}")
            
            # Get device info
            device_info = api.get_device_info()
            if device_info:
                print(f"  Device: {device_info.get('DeviceName', 'Unknown')}")
        else:
            print("✗ Failed to initialize via HTTP")
    except Exception as e:
        print(f"✗ Error: {e}")


def test_https_no_verify():
    """Test HTTPS connection without certificate verification"""
    print("\n" + "="*60)
    print("Testing HTTPS Connection (No Certificate Verification)")
    print("="*60)
    
    # Create API instance with HTTPS but no certificate verification
    api = HiLinkAPI(
        modem_name="TestModem_HTTPS_NoVerify",
        host="192.168.8.1",  # or use hostname if available
        username="admin",
        password="admin",
        logger=logger,
        use_tls=True,      # Enable HTTPS
        verify_tls=False   # Don't verify certificates
    )
    
    print(f"Protocol: {api.protocol}")
    print(f"Base URL: {api.base_url}")
    print(f"Use TLS: {api.use_tls}")
    print(f"Verify TLS: {api.verify_tls}")
    
    try:
        # Initialize API
        if api.initialize():
            print(f"✓ Successfully connected via HTTPS (no cert verification)")
            print(f"  WebUI version: {api.webui_version}")
            
            # Get device info
            device_info = api.get_device_info()
            if device_info:
                print(f"  Device: {device_info.get('DeviceName', 'Unknown')}")
        else:
            print("✗ Failed to initialize via HTTPS")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Note: The modem may not support HTTPS")


def test_https_with_verify():
    """Test HTTPS connection with certificate verification"""
    print("\n" + "="*60)
    print("Testing HTTPS Connection (With Certificate Verification)")
    print("="*60)
    
    # Create API instance with HTTPS and certificate verification
    api = HiLinkAPI(
        modem_name="TestModem_HTTPS_Verify",
        host="192.168.8.1",  # or use hostname if available
        username="admin",
        password="admin",
        logger=logger,
        use_tls=True,      # Enable HTTPS
        verify_tls=True    # Verify certificates
    )
    
    print(f"Protocol: {api.protocol}")
    print(f"Base URL: {api.base_url}")
    print(f"Use TLS: {api.use_tls}")
    print(f"Verify TLS: {api.verify_tls}")
    
    try:
        # Initialize API
        if api.initialize():
            print(f"✓ Successfully connected via HTTPS (with cert verification)")
            print(f"  WebUI version: {api.webui_version}")
            
            # Get device info
            device_info = api.get_device_info()
            if device_info:
                print(f"  Device: {device_info.get('DeviceName', 'Unknown')}")
        else:
            print("✗ Failed to initialize via HTTPS")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Note: This will likely fail with self-signed certificates")


def test_dynamic_protocol_selection():
    """Test dynamic protocol selection based on availability"""
    print("\n" + "="*60)
    print("Testing Dynamic Protocol Selection")
    print("="*60)
    
    host = "192.168.8.1"
    protocols = [
        ("HTTPS with verification", True, True),
        ("HTTPS without verification", True, False),
        ("HTTP", False, False)
    ]
    
    for protocol_name, use_tls, verify_tls in protocols:
        print(f"\nTrying {protocol_name}...")
        
        api = HiLinkAPI(
            modem_name=f"TestModem_{protocol_name.replace(' ', '_')}",
            host=host,
            username="admin",
            password="admin",
            logger=logger,
            use_tls=use_tls,
            verify_tls=verify_tls
        )
        
        try:
            if api.initialize():
                print(f"✓ Success with {protocol_name}")
                print(f"  Base URL: {api.base_url}")
                print(f"  WebUI version: {api.webui_version}")
                
                # Test a simple operation
                wan_ip = api.get_wan_ip()
                print(f"  WAN IP: {wan_ip or 'Not connected'}")
                
                # We found a working protocol, stop trying others
                break
        except Exception as e:
            print(f"✗ Failed with {protocol_name}: {str(e)[:50]}...")
            continue
    else:
        print("\n✗ Could not connect with any protocol")


def test_mixed_operations():
    """Test various operations with TLS configuration"""
    print("\n" + "="*60)
    print("Testing Mixed Operations with TLS Configuration")
    print("="*60)
    
    # Use HTTPS without verification for testing
    api = HiLinkAPI(
        modem_name="TestModem_Operations",
        host="192.168.8.1",
        username="admin",
        password="admin",
        logger=logger,
        use_tls=False,      # Use HTTP for compatibility
        verify_tls=False    # No verification needed for HTTP
    )
    
    try:
        # Initialize
        if not api.initialize():
            print("✗ Failed to initialize API")
            return
        
        print(f"✓ Connected using {api.protocol.upper()}")
        print(f"  WebUI version: {api.webui_version}")
        
        # Check login requirement
        if api.check_login_required():
            print("\n  Authentication required, logging in...")
            if api.login():
                print("  ✓ Login successful")
            else:
                print("  ✗ Login failed")
                return
        
        # Test various operations
        operations = [
            ("Device Info", lambda: api.get_device_info()),
            ("WAN IP", lambda: api.get_wan_ip()),
            ("Network Info", lambda: api.get_network_info()),
            ("Connection Status", lambda: api.get_connection_status()),
            ("Signal Info", lambda: api.get_signal_info()),
            ("SMS Count", lambda: api.get_sms_count())
        ]
        
        print("\n  Testing operations:")
        for op_name, op_func in operations:
            try:
                result = op_func()
                if result:
                    print(f"  ✓ {op_name}: Success")
                else:
                    print(f"  ⚠ {op_name}: No data")
            except Exception as e:
                print(f"  ✗ {op_name}: {str(e)[:30]}...")
        
        # Logout if logged in
        if api.logged_in:
            print("\n  Logging out...")
            if api.logout():
                print("  ✓ Logout successful")
        
    except Exception as e:
        print(f"✗ Error during operations: {e}")


def main():
    """Main test function"""
    print("\n" + "#"*60)
    print("# HiLink API TLS/HTTPS Support Test Suite")
    print("#"*60)
    
    # Test 1: Standard HTTP connection
    test_http_connection()
    
    # Test 2: HTTPS without certificate verification
    test_https_no_verify()
    
    # Test 3: HTTPS with certificate verification
    test_https_with_verify()
    
    # Test 4: Dynamic protocol selection
    test_dynamic_protocol_selection()
    
    # Test 5: Mixed operations with TLS
    test_mixed_operations()
    
    print("\n" + "#"*60)
    print("# Test Suite Completed")
    print("#"*60)
    print("\nSummary:")
    print("- HTTP connections should work by default")
    print("- HTTPS without verification may work if modem supports it")
    print("- HTTPS with verification will likely fail with self-signed certs")
    print("- Use use_tls=False (default) for maximum compatibility")
    print("- Use use_tls=True, verify_tls=False for HTTPS without cert checks")


if __name__ == "__main__":
    main()