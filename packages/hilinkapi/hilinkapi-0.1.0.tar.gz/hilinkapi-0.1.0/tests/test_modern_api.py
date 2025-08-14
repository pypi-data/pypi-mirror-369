#!/usr/bin/env python3
"""
Test script for the modernized HiLink API implementation
"""
import logging
import sys
import os

# Add parent directory to path to import HiLinkAPI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from HiLinkAPI import HiLinkAPI, HiLinkException

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_operations():
    """Test basic API operations"""
    
    # Create API instance
    api = HiLinkAPI(
        modem_name="TestModem",
        host="192.168.8.1",
        username="admin",  # Set your username
        password="admin",  # Set your password
        logger=logger
    )
    
    try:
        # Initialize API (auto-detects WebUI version)
        logger.info("Initializing API...")
        if not api.initialize():
            logger.error("Failed to initialize API")
            return False
        
        logger.info(f"Detected WebUI version: {api.webui_version}")
        
        # Check if login is required
        logger.info("Checking if login is required...")
        if api.check_login_required():
            logger.info("Login is required")
            
            # Perform login
            logger.info("Attempting login...")
            if not api.login():
                logger.error("Login failed")
                return False
            logger.info("Login successful")
        else:
            logger.info("Login not required")
        
        # Get device information
        logger.info("Getting device information...")
        device_info = api.get_device_info()
        if device_info:
            logger.info(f"Device Name: {device_info.get('DeviceName', 'Unknown')}")
            logger.info(f"IMEI: {device_info.get('Imei', 'Unknown')}")
            logger.info(f"Software Version: {device_info.get('SoftwareVersion', 'Unknown')}")
            logger.info(f"Hardware Version: {device_info.get('HardwareVersion', 'Unknown')}")
        
        # Get WAN IP
        logger.info("Getting WAN IP...")
        wan_ip = api.get_wan_ip()
        logger.info(f"WAN IP: {wan_ip or 'Not connected'}")
        
        # Get network information
        logger.info("Getting network information...")
        network_info = api.get_network_info()
        if network_info:
            logger.info(f"Network Name: {network_info.get('FullName', 'Unknown')}")
            logger.info(f"Network State: {network_info.get('State', 'Unknown')}")
        
        # Get connection status
        logger.info("Getting connection status...")
        conn_status = api.get_connection_status()
        if conn_status:
            logger.info(f"Connection Status: {conn_status.get('ConnectionStatus', 'Unknown')}")
            logger.info(f"Signal Strength: {conn_status.get('SignalStrength', 'Unknown')}")
        
        # Get signal information
        logger.info("Getting signal information...")
        signal_info = api.get_signal_info()
        if signal_info:
            logger.info(f"RSSI: {signal_info.get('rssi', 'Unknown')}")
            logger.info(f"RSRP: {signal_info.get('rsrp', 'Unknown')}")
            logger.info(f"RSRQ: {signal_info.get('rsrq', 'Unknown')}")
            logger.info(f"SINR: {signal_info.get('sinr', 'Unknown')}")
        
        # Get SMS count
        logger.info("Getting SMS count...")
        sms_count = api.get_sms_count()
        logger.info(f"SMS - Unread: {sms_count['unread']}, Inbox: {sms_count['inbox']}")
        
        # Logout if we logged in
        if api.logged_in:
            logger.info("Logging out...")
            if api.logout():
                logger.info("Logout successful")
            else:
                logger.warning("Logout failed")
        
        return True
        
    except HiLinkException as e:
        logger.error(f"HiLink API error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def test_connection_management():
    """Test connection management operations"""
    
    # Create API instance
    api = HiLinkAPI(
        modem_name="TestModem",
        host="192.168.8.1",
        username="admin",
        password="admin",
        logger=logger
    )
    
    try:
        # Initialize and login
        if not api.initialize():
            return False
        
        if api.check_login_required() and not api.login():
            return False
        
        # Test switching connection
        logger.info("Testing connection switch...")
        
        # Disable connection
        logger.info("Disabling data connection...")
        if api.switch_connection(False):
            logger.info("Data connection disabled")
        else:
            logger.warning("Failed to disable data connection")
        
        # Enable connection
        logger.info("Enabling data connection...")
        if api.switch_connection(True):
            logger.info("Data connection enabled")
        else:
            logger.warning("Failed to enable data connection")
        
        # Test network mode switching
        logger.info("Testing network mode switch...")
        
        # Switch to LTE
        logger.info("Switching to LTE mode...")
        if api.switch_network_mode("LTE"):
            logger.info("Switched to LTE mode")
        else:
            logger.warning("Failed to switch to LTE mode")
        
        # Configure data connection
        logger.info("Configuring data connection...")
        if api.configure_data_connection(roaming=True, max_idle_time=3600):
            logger.info("Data connection configured")
        else:
            logger.warning("Failed to configure data connection")
        
        # Logout
        if api.logged_in:
            api.logout()
        
        return True
        
    except Exception as e:
        logger.error(f"Error in connection management test: {e}")
        return False


def test_manual_version_selection():
    """Test manual WebUI version selection"""
    
    logger.info("Testing manual version selection...")
    
    # Manually set implementation to WebUI 10
    HiLinkAPI.set_implementation(10)
    logger.info("Set implementation to WebUI 10")
    
    api = HiLinkAPI(
        modem_name="TestModem",
        host="192.168.8.1",
        username="admin",
        password="admin",
        logger=logger
    )
    
    # The API will use the manually set implementation
    impl = HiLinkAPI.get_implementation()
    logger.info(f"Current implementation: {impl.__class__.__name__}")
    
    # You can also change implementation at runtime
    HiLinkAPI.set_implementation(17)
    logger.info("Changed implementation to WebUI 17")
    
    impl = HiLinkAPI.get_implementation()
    logger.info(f"Current implementation: {impl.__class__.__name__}")
    
    return True


def main():
    """Main test function"""
    
    logger.info("=" * 60)
    logger.info("Starting HiLink API Modern Implementation Tests")
    logger.info("=" * 60)
    
    # Test basic operations
    logger.info("\n--- Testing Basic Operations ---")
    if test_basic_operations():
        logger.info("Basic operations test PASSED")
    else:
        logger.error("Basic operations test FAILED")
    
    # Test connection management
    logger.info("\n--- Testing Connection Management ---")
    if test_connection_management():
        logger.info("Connection management test PASSED")
    else:
        logger.error("Connection management test FAILED")
    
    # Test manual version selection
    logger.info("\n--- Testing Manual Version Selection ---")
    if test_manual_version_selection():
        logger.info("Manual version selection test PASSED")
    else:
        logger.error("Manual version selection test FAILED")
    
    logger.info("\n" + "=" * 60)
    logger.info("Tests completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()