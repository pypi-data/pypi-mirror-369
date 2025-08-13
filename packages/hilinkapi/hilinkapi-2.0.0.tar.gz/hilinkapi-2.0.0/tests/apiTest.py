from HiLinkAPI_modern import HiLinkAPI, HiLinkException
import logging
from time import sleep, time
from datetime import datetime


def main():
    logging.basicConfig(
        filename="hilinkapitest.log", 
        format='%(asctime)s --  %(name)s::%(levelname)s -- {%(pathname)s:%(lineno)d} -- %(message)s', 
        level=logging.DEBUG, 
        datefmt="%Y-%m-%d %I:%M:%S %p:%Z"
    )

    try:
        # Create API instances for different modems
        modem_configs = [
            # {"name": "E3372h-153", "host": "192.168.8.1", "username": None, "password": None},
            {"name": "E3372h-320", "host": "192.168.8.1", "username": None, "password": None},
            # {"name": "E8372h-320", "host": "192.168.10.1", "username": "admin", "password": "abcd@1234"},
        ]
        
        for config in modem_configs:
            api = HiLinkAPI(
                modem_name=config["name"],
                host=config["host"],
                username=config.get("username"),
                password=config.get("password"),
                logger=logging.getLogger(config["name"])
            )
            
            try:
                print(f"\n{'='*50}")
                print(f"Testing modem: {config['name']} at {config['host']}")
                print(f"{'='*50}")
                
                # Initialize API (replaces webUI.start())
                print("Initializing API...")
                if not api.initialize():
                    print(f"Failed to initialize API for {config['name']}")
                    continue
                
                print(f"✓ API initialized - WebUI version: {api.webui_version}")
                
                # Check if login is required and login if needed
                if api.check_login_required():
                    print("Login required, attempting login...")
                    
                    # Check login state first
                    login_state = api.get_login_state()
                    if login_state.get("remain_wait_time", 0) > 0:
                        print(f"Login wait time available = {login_state['remain_wait_time']} seconds")
                        sleep(5)
                        continue
                    
                    # Attempt login
                    if api.login():
                        print("✓ Login successful")
                    else:
                        print("✗ Login failed")
                        # Check for errors
                        if api.last_error_code:
                            print(f"Error: {api.last_error_code} - {api.last_error_message}")
                        continue
                else:
                    print("Login not required")
                
                print("\n" + "-"*40)
                print("Configuring and Testing Connection")
                print("-"*40)
                
                # Configure data connection (replaces webUI.configureDataConnection)
                print("Configuring data connection...")
                if api.configure_data_connection(roaming=True, max_idle_time=0):
                    print("✓ Data roaming enabled, disable idle timeout")
                
                # Get device information (replaces webUI.queryDeviceInfo)
                print("\nQuerying device information...")
                device_info = api.get_device_info(use_cache=False)
                
                # Get WAN IP (replaces webUI.queryWANIP)
                wan_ip = api.get_wan_ip()
                
                # Get network info (replaces webUI.queryNetwork)
                network_info = api.get_network_info(use_cache=False)
                
                # Get connection status
                conn_status = api.get_connection_status()
                
                print("\n" + "-"*40)
                print("Device Information")
                print("-"*40)
                
                # Display device info (replaces webUI.getDeviceName(), etc.)
                print(f"Device name: {device_info.get('DeviceName', 'Unknown')}")
                print(f"WebUI version: {api.webui_version}")
                print(f"Login required: {api.login_required}")
                print(f"Valid session: {api.logged_in or not api.login_required}")
                
                print("\n" + "-"*40)
                print("Connection Information")
                print("-"*40)
                
                # Display connection info
                print(f"WAN IP: {wan_ip or 'Not connected'}")
                print(f"Network: {network_info.get('FullName', 'Unknown')}")
                print(f"Connection Status: {conn_status.get('ConnectionStatus', 'Unknown')}")
                
                # Display detailed device info
                print("\n" + "-"*40)
                print("Detailed Device Information")
                print("-"*40)
                
                for key, value in device_info.items():
                    # Format output with tabs for alignment
                    tabs = "\t\t" if len(key) < 8 else "\t"
                    print(f"{key}{tabs}: {value}")
                
                print("\n" + "-"*40)
                print("Network Mode Configuration")
                print("-"*40)
                
                # Test network mode switching (simplified from old setNetwokModes)
                print("Testing network mode switching...")
                modes_to_test = ["LTE", "WCDMA", "AUTO"]
                
                for mode in modes_to_test:
                    print(f"  Setting network mode to {mode}...")
                    if api.switch_network_mode(mode):
                        print(f"  ✓ Successfully set to {mode}")
                    else:
                        print(f"  ✗ Failed to set to {mode}")
                    sleep(1)
                
                print("\n" + "-"*40)
                print("Connection On/Off Test")
                print("-"*40)
                
                # Test connection switching (replaces webUI.switchConnection)
                print(f"Current time: {datetime.now()}")
                print(f"Current WAN IP: {api.get_wan_ip()}")
                
                print("Switching connection OFF...")
                if api.switch_connection(enable=False):
                    print("✓ Connection disabled")
                    sleep(1)
                
                print("Switching connection ON...")
                if api.switch_connection(enable=True):
                    print("✓ Connection enabled")
                    
                    # Wait for new IP
                    print("Waiting for new WAN IP...")
                    max_wait = 30  # Maximum 30 seconds
                    wait_time = 0
                    while wait_time < max_wait:
                        wan_ip = api.get_wan_ip()
                        if wan_ip:
                            print(f"✓ New WAN IP: {wan_ip}")
                            break
                        sleep(2)
                        wait_time += 2
                    else:
                        print("✗ Timeout waiting for WAN IP")
                
                # Optional: Test network mode rotation (commented out like in original)
                # Uncomment to test network mode rotation
                """
                print("\n" + "-"*40)
                print("Network Mode Rotation Test")
                print("-"*40)
                
                rotation_count = 1  # Number of rotations to perform
                for i in range(rotation_count):
                    print(f"\nRotation {i+1}/{rotation_count}")
                    print(f"Time: {datetime.now()}")
                    
                    # Switch to WCDMA
                    print("Switching to WCDMA...")
                    if api.switch_network_mode("WCDMA"):
                        print("✓ Switched to WCDMA")
                    sleep(1)
                    
                    # Switch back to LTE
                    print("Switching to LTE...")
                    if api.switch_network_mode("LTE"):
                        print("✓ Switched to LTE")
                    
                    # Wait for reconnection
                    print("Waiting for reconnection...")
                    max_wait = 30
                    wait_time = 0
                    while wait_time < max_wait:
                        wan_ip = api.get_wan_ip()
                        if wan_ip:
                            print(f"✓ Reconnected with IP: {wan_ip}")
                            break
                        sleep(2)
                        wait_time += 2
                    
                    if i < rotation_count - 1:
                        print(f"Waiting 60 seconds before next rotation...")
                        sleep(60)
                """
                
                # Optional: Test reboot (commented out like in original)
                # print("\nRebooting modem...")
                # if api.reboot():
                #     print("✓ Reboot initiated")
                
                print("\n" + "*"*50)
                print(f"Testing completed for {config['name']}")
                print("*"*50)
                
                # Logout if we logged in (replaces webUI.stop())
                if api.logged_in:
                    print("\nLogging out...")
                    if api.logout():
                        print("✓ Logged out successfully")
                    else:
                        print("✗ Logout failed")
                
            except HiLinkException as e:
                print(f"HiLink API Error: {e}")
                logging.error(f"HiLink API Error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
                logging.error(f"Unexpected error: {e}", exc_info=True)
            
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}", exc_info=True)
    
    # End of the test
    print("\n" + "="*50)
    print("All tests completed")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()