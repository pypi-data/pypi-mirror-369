"""
Huawei HiLink API - Modern Python implementation for Huawei HiLink modems.

This module provides a comprehensive API for interacting with Huawei HiLink modems
across different WebUI versions (10, 17, and 21). It automatically detects the modem's
WebUI version and uses the appropriate implementation.

Features:
    - Automatic WebUI version detection
    - Support for WebUI versions 10, 17, and 21
    - TLS/SSL support for secure connections
    - Session management with automatic token refresh
    - Comprehensive error handling
    - Device information retrieval
    - Network management (mode switching, connection control)
    - SMS count monitoring
    - Signal strength monitoring
    - Data connection configuration

Example:
    >>> from HiLinkAPI import HiLinkAPI
    >>> api = HiLinkAPI("MyModem", "192.168.8.1", "admin", "password")
    >>> api.initialize()
    >>> device_info = api.get_device_info()
    >>> print(device_info)

Author: HiLink API Contributors
License: MIT
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
import requests
import xmltodict
import uuid
import base64
import hashlib
import binascii
import hmac
from binascii import hexlify
from collections import OrderedDict
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3

# Disable SSL warnings when verify_tls is False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HiLinkException(Exception):
    """
    Custom exception for HiLink API errors.
    
    This exception is raised when API operations fail, providing context
    about which modem experienced the error and what went wrong.
    
    Attributes:
        modem_name (str): The name/identifier of the modem that experienced the error
        message (str): Detailed error message describing what went wrong
    """
    
    def __init__(self, modem_name: str, message: str):
        """
        Initialize HiLinkException.
        
        Args:
            modem_name: Identifier for the modem that experienced the error
            message: Detailed error message
        """
        self.message = message
        self.modem_name = modem_name
        super().__init__(f"Huawei HiLink API Error ({modem_name}): {message}")


class HiLinkAPIInterface(ABC):
    """
    Abstract base class defining the HiLink API interface.
    
    This interface defines all methods that must be implemented by version-specific
    implementations (WebUI 10, 17, 21). It ensures consistency across different
    WebUI versions while allowing for version-specific implementation details.
    
    Attributes:
        ERROR_CODES (dict): Mapping of numeric error codes to human-readable error messages
    """
    
    # Error codes common to all versions
    ERROR_CODES = {
        # System errors
        100002: "ERROR_SYSTEM_NO_SUPPORT",
        100003: "ERROR_SYSTEM_NO_RIGHTS",
        100004: "ERROR_BUSY",
        # Authentication errors
        108001: "ERROR_LOGIN_USERNAME_WRONG",
        108002: "ERROR_LOGIN_PASSWORD_WRONG",
        108003: "ERROR_LOGIN_ALREADY_LOGIN",
        108005: "ERROR_LOGIN_TOO_MANY_USERS_LOGINED",
        108006: "ERROR_LOGIN_USERNAME_OR_PASSWORD_ERROR",
        108007: "ERROR_LOGIN_TOO_MANY_TIMES",
        108008: "MODIFYPASSWORD_ERROR",
        108009: "ERROR_LOGIN_IN_DEFFERENT_DEVICES",
        108010: "ERROR_LOGIN_FREQUENTLY_LOGIN",
        # SIM errors
        101001: "ERROR_NO_SIM_CARD_OR_INVALID_SIM_CARD",
        101002: "ERROR_CHECK_SIM_CARD_PIN_LOCK",
        101003: "ERROR_CHECK_SIM_CARD_PUN_LOCK",
        101004: "ERROR_CHECK_SIM_CARD_CAN_UNUSEABLE",
        101005: "ERROR_ENABLE_PIN_FAILED",
        101006: "ERROR_DISABLE_PIN_FAILED",
        101007: "ERROR_UNLOCK_PIN_FAILED",
        101008: "ERROR_DISABLE_AUTO_PIN_FAILED",
        101009: "ERROR_ENABLE_AUTO_PIN_FAILED",
        103002: "ERROR_DEVICE_PIN_VALIDATE_FAILED",
        103003: "ERROR_DEVICE_PIN_MODIFFY_FAILED",
        103004: "ERROR_DEVICE_PUK_MODIFFY_FAILED",
        103008: "ERROR_DEVICE_SIM_CARD_BUSY",
        103009: "ERROR_DEVICE_SIM_LOCK_INPUT_ERROR",
        103011: "ERROR_DEVICE_PUK_DEAD_LOCK",
        # Network errors
        112001: "ERROR_SET_NET_MODE_AND_BAND_WHEN_DAILUP_FAILED",
        112002: "ERROR_SET_NET_SEARCH_MODE_WHEN_DAILUP_FAILED",
        112003: "ERROR_SET_NET_MODE_AND_BAND_FAILED",
        112005: "ERROR_NET_REGISTER_NET_FAILED",
        112008: "ERROR_NET_SIM_CARD_NOT_READY_STATUS",
        # Session errors
        125001: "ERROR_WRONG_TOKEN",
        125002: "ERROR_WRONG_SESSION",
        125003: "ERROR_WRONG_SESSION_TOKEN",
    }
    
    @abstractmethod
    def initialize_session(self, base_url: str, session_id: Optional[str], token: Optional[str], verify_ssl: bool = False) -> Tuple[str, str]:
        """
        Initialize a session with the modem.
        
        Args:
            base_url: The base URL of the modem (e.g., http://192.168.8.1)
            session_id: Existing session ID to reuse (optional)
            token: Existing token to reuse (optional)
            verify_ssl: Whether to verify SSL certificates
            
        Returns:
            Tuple of (session_id, token) for use in subsequent API calls
            
        Raises:
            HiLinkException: If session initialization fails
        """
        pass
    
    @abstractmethod
    def login(self, base_url: str, username: str, password: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """
        Perform login authentication.
        
        Args:
            base_url: The base URL of the modem
            username: Login username
            password: Login password
            session_id: Current session ID
            token: Current verification token
            verify_ssl: Whether to verify SSL certificates
            
        Returns:
            True if login successful, False otherwise
        """
        pass
    
    @abstractmethod
    def logout(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Perform logout and return success status"""
        pass
    
    @abstractmethod
    def get_device_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive device information.
        
        Args:
            base_url: The base URL of the modem
            session_id: Current session ID
            token: Current verification token
            verify_ssl: Whether to verify SSL certificates
            
        Returns:
            Dictionary containing device information including:
                - DeviceName: Model name of the device
                - SerialNumber: Device serial number
                - Imei: IMEI number
                - Imsi: IMSI number
                - Iccid: SIM card ICCID
                - HardwareVersion: Hardware version
                - SoftwareVersion: Firmware version
                - WebUIVersion: WebUI version
                - And other device-specific fields
        """
        pass
    
    @abstractmethod
    def get_wan_ip(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Optional[str]:
        """Get WAN IP address"""
        pass
    
    @abstractmethod
    def get_network_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get network information"""
        pass
    
    @abstractmethod
    def get_connection_status(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get connection status"""
        pass
    
    @abstractmethod
    def switch_connection(self, base_url: str, session_id: str, token: str, enable: bool, verify_ssl: bool = False) -> bool:
        """Switch data connection on/off"""
        pass
    
    @abstractmethod
    def switch_network_mode(self, base_url: str, session_id: str, token: str, mode: str, verify_ssl: bool = False) -> bool:
        """Switch network mode (LTE/WCDMA/GSM)"""
        pass
    
    @abstractmethod
    def configure_data_connection(self, base_url: str, session_id: str, token: str,
                                 roaming: bool, max_idle_time: int, verify_ssl: bool = False) -> bool:
        """Configure data connection settings"""
        pass
    
    @abstractmethod
    def reboot(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Reboot the modem"""
        pass
    
    @abstractmethod
    def get_signal_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get signal strength information"""
        pass
    
    @abstractmethod
    def get_sms_count(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, int]:
        """Get SMS count information"""
        pass
    
    @abstractmethod
    def check_login_required(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Check if login is required"""
        pass
    
    @abstractmethod
    def get_login_state(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get current login state"""
        pass


class WebUI10Implementation(HiLinkAPIInterface):
    """
    WebUI version 10 implementation.
    
    This class implements the HiLink API for modems running WebUI version 10.x.
    It uses challenge-response authentication with PBKDF2-HMAC-SHA256 for secure login.
    
    The implementation handles:
        - Token-based session management
        - Challenge-response authentication
        - XML-based API communication
        - Version-specific API endpoints
    """
    
    @staticmethod
    def _login_b64_sha256(data: str) -> str:
        """
        Perform SHA256 hashing and base64 encoding for authentication.
        
        This method is used in the WebUI 10 authentication process to hash
        passwords and other sensitive data.
        
        Args:
            data: The string data to hash and encode
            
        Returns:
            Base64-encoded SHA256 hash of the input data
        """
        s256 = hashlib.sha256()
        s256.update(data.encode('utf-8'))
        dg = s256.digest()
        hs256 = binascii.hexlify(dg)
        return base64.urlsafe_b64encode(hs256).decode('utf-8', 'ignore')
    
    @staticmethod
    def _http_request(method: str, url: str, headers: Optional[Dict] = None,
                     cookies: Optional[Dict] = None, data: Optional[str] = None,
                     timeout: int = 10, verify_ssl: bool = False) -> requests.Response:
        """Make HTTP request with proper error handling and SSL support"""
        try:
            if method.upper() == "GET":
                return requests.get(url, headers=headers, cookies=cookies,
                                  timeout=timeout, verify=verify_ssl)
            else:
                return requests.post(url, headers=headers, cookies=cookies,
                                   data=data, timeout=timeout, verify=verify_ssl)
        except requests.RequestException as e:
            raise HiLinkException("WebUI10", f"HTTP request failed: {e}")
    
    def initialize_session(self, base_url: str, session_id: Optional[str], token: Optional[str], verify_ssl: bool = False) -> Tuple[str, str]:
        """Initialize session for WebUI 10"""
        # Get initial session
        response = self._http_request("GET", f"{base_url}/", verify_ssl=verify_ssl)
        
        # Extract session ID from cookies
        new_session_id = response.cookies.get('SessionID', session_id)
        
        # Get token
        response = self._http_request("GET", f"{base_url}/api/webserver/token",
                                     cookies={'SessionID': new_session_id} if new_session_id else None,
                                     verify_ssl=verify_ssl)
        
        token_data = xmltodict.parse(response.text)
        if "response" in token_data and "token" in token_data["response"]:
            login_token = token_data['response']['token']
            new_token = login_token[-32:]  # Last 32 characters
            return new_session_id, new_token
        
        raise HiLinkException("WebUI10", "Failed to initialize session")
    
    def login(self, base_url: str, username: str, password: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Perform login for WebUI 10"""
        # Get fresh token for login
        response = self._http_request("GET", f"{base_url}/api/webserver/token",
                                     cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        token_data = xmltodict.parse(response.text)
        if "response" in token_data:
            tmp_token = token_data['response']['token']
            token = tmp_token[-32:]
        
        # Challenge login
        client_nonce = uuid.uuid4().hex + uuid.uuid4().hex
        
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<username>{username}</username>
<firstnonce>{client_nonce}</firstnonce>
<mode>1</mode>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/user/challenge_login",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        challenge_dict = xmltodict.parse(response.text)
        
        if 'response' not in challenge_dict:
            return False
        
        salt = challenge_dict['response']['salt']
        server_nonce = challenge_dict['response']['servernonce']
        iterations = int(challenge_dict['response']['iterations'])
        
        # Authenticate login
        msg = f"{client_nonce},{server_nonce},{server_nonce}"
        salted_pass = hashlib.pbkdf2_hmac('sha256', bytearray(password.encode('utf-8')), 
                                         bytearray.fromhex(salt), iterations)
        client_key = hmac.new(b'Client Key', msg=salted_pass, digestmod=hashlib.sha256)
        stored_key = hashlib.sha256()
        stored_key.update(client_key.digest())
        signature = hmac.new(msg.encode('utf_8'), msg=stored_key.digest(), digestmod=hashlib.sha256)
        
        client_proof = bytearray()
        for i in range(client_key.digest_size):
            val = client_key.digest()[i] ^ signature.digest()[i]
            client_proof.append(val)
        
        hex_client_proof = hexlify(client_proof).decode()
        
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<clientproof>{hex_client_proof}</clientproof>
<finalnonce>{server_nonce}</finalnonce>
</request>"""
        
        response = self._http_request("POST", f"{base_url}/api/user/authentication_login",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        login_response = xmltodict.parse(response.text)
        return "response" in login_response
    
    def logout(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Perform logout for WebUI 10"""
        xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<request>
<Logout>1</Logout>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/user/logout",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        logout_response = xmltodict.parse(response.text)
        return "response" in logout_response
    
    def get_device_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get device information for WebUI 10"""
        headers = {
            '__RequestVerificationToken': token,
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = self._http_request("GET", f"{base_url}/api/device/information",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        device_info = xmltodict.parse(response.text)
        if "response" in device_info:
            return device_info["response"]
        return {}
    
    def get_wan_ip(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Optional[str]:
        """Get WAN IP for WebUI 10"""
        device_info = self.get_device_info(base_url, session_id, token, verify_ssl)
        return device_info.get("WanIPAddress")
    
    def get_network_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get network information for WebUI 10"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/net/current-plmn",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        network_info = xmltodict.parse(response.text)
        if "response" in network_info:
            return network_info["response"]
        return {}
    
    def get_connection_status(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get connection status for WebUI 10"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/monitoring/status",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        status_info = xmltodict.parse(response.text)
        if "response" in status_info:
            return status_info["response"]
        return {}
    
    def switch_connection(self, base_url: str, session_id: str, token: str, enable: bool, verify_ssl: bool = False) -> bool:
        """Switch data connection for WebUI 10"""
        data_switch = "1" if enable else "0"
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<dataswitch>{data_switch}</dataswitch>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/dialup/mobile-dataswitch",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        switch_info = xmltodict.parse(response.text)
        return "response" in switch_info
    
    def switch_network_mode(self, base_url: str, session_id: str, token: str, mode: str, verify_ssl: bool = False) -> bool:
        """Switch network mode for WebUI 10"""
        mode_map = {"LTE": "03", "WCDMA": "02", "GSM": "01", "AUTO": "00"}
        network_mode = mode_map.get(mode.upper(), "00")
        
        # Get current band settings
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        response = self._http_request("GET", f"{base_url}/api/net/net-mode",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        net_mode_info = xmltodict.parse(response.text)
        if "response" not in net_mode_info:
            return False
        
        network_band = net_mode_info['response'].get('NetworkBand', '')
        lte_band = net_mode_info['response'].get('LTEBand', '')
        
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<NetworkMode>{network_mode}</NetworkMode>
<NetworkBand>{network_band}</NetworkBand>
<LTEBand>{lte_band}</LTEBand>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/net/net-mode",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        switch_info = xmltodict.parse(response.text)
        return "response" in switch_info
    
    def configure_data_connection(self, base_url: str, session_id: str, token: str,
                                 roaming: bool, max_idle_time: int, verify_ssl: bool = False) -> bool:
        """Configure data connection for WebUI 10"""
        data_roaming = "1" if roaming else "0"
        
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<RoamAutoConnectEnable>{data_roaming}</RoamAutoConnectEnable>
<MaxIdelTime>{max_idle_time}</MaxIdelTime>
<ConnectMode>0</ConnectMode>
<MTU>1500</MTU>
<auto_dial_switch>1</auto_dial_switch>
<pdp_always_on>0</pdp_always_on>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/dialup/connection",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        config_info = xmltodict.parse(response.text)
        return "response" in config_info
    
    def reboot(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Reboot modem for WebUI 10"""
        xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<request>
<Control>1</Control>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        try:
            self._http_request("POST", f"{base_url}/api/device/control",
                             headers=headers, cookies={'SessionID': session_id},
                             data=xml_body, timeout=3, verify_ssl=verify_ssl)
            return True
        except:
            # Reboot causes connection to drop, which is expected
            return True
    
    def get_signal_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get signal information for WebUI 10"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/device/signal",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        signal_info = xmltodict.parse(response.text)
        if "response" in signal_info:
            return signal_info["response"]
        return {}
    
    def get_sms_count(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, int]:
        """Get SMS count for WebUI 10"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/sms/sms-count",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        sms_info = xmltodict.parse(response.text)
        if "response" in sms_info:
            return {
                "unread": int(sms_info["response"].get("LocalUnread", 0)),
                "inbox": int(sms_info["response"].get("LocalInbox", 0)),
                "outbox": int(sms_info["response"].get("LocalOutbox", 0)),
                "draft": int(sms_info["response"].get("LocalDraft", 0))
            }
        return {"unread": 0, "inbox": 0, "outbox": 0, "draft": 0}
    
    def check_login_required(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Check if login is required for WebUI 10"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/user/hilink_login",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        hilink_login = xmltodict.parse(response.text)
        if "response" in hilink_login:
            return int(hilink_login['response'].get('hilink_login', 0)) == 1
        return False
    
    def get_login_state(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get login state for WebUI 10"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/user/state-login",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        state_login = xmltodict.parse(response.text)
        if "response" in state_login:
            return {
                "logged_in": int(state_login['response'].get('State', -1)) == 0,
                "password_type": state_login['response'].get('password_type', ''),
                "remain_wait_time": int(state_login['response'].get('remainwaittime', 0))
            }
        return {"logged_in": False, "password_type": "", "remain_wait_time": 0}


class WebUI17Implementation(HiLinkAPIInterface):
    """
    WebUI version 17 implementation.
    
    This class implements the HiLink API for modems running WebUI version 17.x.
    It uses a different authentication mechanism than WebUI 10, with tokens
    extracted from HTML meta tags and simpler password hashing.
    
    Key differences from WebUI 10:
        - Token extraction from HTML meta tags
        - Different password hashing algorithm
        - Different WAN IP endpoint (/api/monitoring/status)
        - Simplified authentication flow
    """
    
    @staticmethod
    def _http_request(method: str, url: str, headers: Optional[Dict] = None,
                     cookies: Optional[Dict] = None, data: Optional[str] = None,
                     timeout: int = 10, verify_ssl: bool = False) -> requests.Response:
        """
        Make HTTP request with proper error handling and SSL support.
        
        Args:
            method: HTTP method (GET or POST)
            url: Full URL to request
            headers: Optional HTTP headers
            cookies: Optional cookies to send
            data: Optional request body (for POST requests)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
            
        Returns:
            Response object from the HTTP request
            
        Raises:
            HiLinkException: If the HTTP request fails
        """
        try:
            if method.upper() == "GET":
                return requests.get(url, headers=headers, cookies=cookies,
                                  timeout=timeout, verify=verify_ssl)
            else:
                return requests.post(url, headers=headers, cookies=cookies,
                                   data=data, timeout=timeout, verify=verify_ssl)
        except requests.RequestException as e:
            raise HiLinkException("WebUI17", f"HTTP request failed: {e}")
    
    def initialize_session(self, base_url: str, session_id: Optional[str], token: Optional[str], verify_ssl: bool = False) -> Tuple[str, str]:
        """Initialize session for WebUI 17"""
        # Get initial session
        response = self._http_request("GET", f"{base_url}/", verify_ssl=verify_ssl)
        
        # Extract session ID from cookies
        new_session_id = response.cookies.get('SessionID', session_id)
        
        # Get token from HTML page
        response = self._http_request("GET", f"{base_url}/html/home.html",
                                     cookies={'SessionID': new_session_id} if new_session_id else None,
                                     verify_ssl=verify_ssl)
        
        soup = BeautifulSoup(response.text, "html.parser")
        meta = soup.head.find("meta", {"name": "csrf_token"})
        if meta:
            new_token = meta.get("content", "")
            if new_token:
                return new_session_id, new_token
        
        raise HiLinkException("WebUI17", "Failed to initialize session")
    
    def login(self, base_url: str, username: str, password: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Perform login for WebUI 17"""
        # Generate password hash
        passwd_string = password
        s256 = hashlib.sha256()
        s256.update(passwd_string.encode('utf-8'))
        dg = s256.digest()
        hs256 = binascii.hexlify(dg)
        hashed_password = base64.urlsafe_b64encode(hs256).decode('utf-8', 'ignore')
        
        s2562 = hashlib.sha256()
        s2562.update(f"{username}{hashed_password}{token}".encode('utf-8'))
        dg2 = s2562.digest()
        hs2562 = binascii.hexlify(dg2)
        hashed_username_password = base64.urlsafe_b64encode(hs2562).decode('utf-8', 'ignore')
        
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<Username>{username}</Username>
<Password>{hashed_username_password}</Password>
<password_type>4</password_type>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/user/login",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        login_response = xmltodict.parse(response.text)
        return "response" in login_response and login_response["response"] == "OK"
    
    def logout(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Perform logout for WebUI 17"""
        xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<request>
<Logout>1</Logout>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/user/logout",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        logout_response = xmltodict.parse(response.text)
        return "response" in logout_response
    
    def get_device_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get device information for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/device/information",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        device_info = xmltodict.parse(response.text)
        if "response" in device_info:
            return device_info["response"]
        return {}
    
    def get_wan_ip(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Optional[str]:
        """Get WAN IP for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/monitoring/status",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        status_info = xmltodict.parse(response.text)
        if "response" in status_info:
            return status_info["response"].get("WanIPAddress")
        return None
    
    def get_network_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get network information for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/net/current-plmn",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        network_info = xmltodict.parse(response.text)
        if "response" in network_info:
            return network_info["response"]
        return {}
    
    def get_connection_status(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get connection status for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/monitoring/status",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        status_info = xmltodict.parse(response.text)
        if "response" in status_info:
            return status_info["response"]
        return {}
    
    def switch_connection(self, base_url: str, session_id: str, token: str, enable: bool, verify_ssl: bool = False) -> bool:
        """Switch data connection for WebUI 17"""
        data_switch = "1" if enable else "0"
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<dataswitch>{data_switch}</dataswitch>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/dialup/mobile-dataswitch",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        switch_info = xmltodict.parse(response.text)
        return "response" in switch_info
    
    def switch_network_mode(self, base_url: str, session_id: str, token: str, mode: str, verify_ssl: bool = False) -> bool:
        """Switch network mode for WebUI 17"""
        mode_map = {"LTE": "03", "WCDMA": "02", "GSM": "01", "AUTO": "00"}
        network_mode = mode_map.get(mode.upper(), "00")
        
        # Get current band settings
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        response = self._http_request("GET", f"{base_url}/api/net/net-mode",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        net_mode_info = xmltodict.parse(response.text)
        if "response" not in net_mode_info:
            return False
        
        network_band = net_mode_info['response'].get('NetworkBand', '')
        lte_band = net_mode_info['response'].get('LTEBand', '')
        
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<NetworkMode>{network_mode}</NetworkMode>
<NetworkBand>{network_band}</NetworkBand>
<LTEBand>{lte_band}</LTEBand>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/net/net-mode",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        switch_info = xmltodict.parse(response.text)
        return "response" in switch_info
    
    def configure_data_connection(self, base_url: str, session_id: str, token: str,
                                 roaming: bool, max_idle_time: int, verify_ssl: bool = False) -> bool:
        """Configure data connection for WebUI 17"""
        data_roaming = "1" if roaming else "0"
        
        xml_body = f"""<?xml version="1.0" encoding="UTF-8"?>
<request>
<RoamAutoConnectEnable>{data_roaming}</RoamAutoConnectEnable>
<MaxIdelTime>{max_idle_time}</MaxIdelTime>
<ConnectMode>0</ConnectMode>
<MTU>1500</MTU>
<auto_dial_switch>1</auto_dial_switch>
<pdp_always_on>0</pdp_always_on>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        response = self._http_request("POST", f"{base_url}/api/dialup/connection",
                                     headers=headers, cookies={'SessionID': session_id},
                                     data=xml_body, verify_ssl=verify_ssl)
        
        config_info = xmltodict.parse(response.text)
        return "response" in config_info
    
    def reboot(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Reboot modem for WebUI 17"""
        xml_body = """<?xml version="1.0" encoding="UTF-8"?>
<request>
<Control>1</Control>
</request>"""
        
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            '__RequestVerificationToken': token
        }
        
        try:
            self._http_request("POST", f"{base_url}/api/device/control",
                             headers=headers, cookies={'SessionID': session_id},
                             data=xml_body, timeout=3, verify_ssl=verify_ssl)
            return True
        except:
            # Reboot causes connection to drop, which is expected
            return True
    
    def get_signal_info(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get signal information for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/device/signal",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        signal_info = xmltodict.parse(response.text)
        if "response" in signal_info:
            return signal_info["response"]
        return {}
    
    def get_sms_count(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, int]:
        """Get SMS count for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/sms/sms-count",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        sms_info = xmltodict.parse(response.text)
        if "response" in sms_info:
            return {
                "unread": int(sms_info["response"].get("LocalUnread", 0)),
                "inbox": int(sms_info["response"].get("LocalInbox", 0)),
                "outbox": int(sms_info["response"].get("LocalOutbox", 0)),
                "draft": int(sms_info["response"].get("LocalDraft", 0))
            }
        return {"unread": 0, "inbox": 0, "outbox": 0, "draft": 0}
    
    def check_login_required(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> bool:
        """Check if login is required for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/user/hilink_login",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        hilink_login = xmltodict.parse(response.text)
        if "response" in hilink_login:
            return int(hilink_login['response'].get('hilink_login', 0)) == 1
        return False
    
    def get_login_state(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Dict[str, Any]:
        """Get login state for WebUI 17"""
        headers = {'X-Requested-With': 'XMLHttpRequest'}
        
        response = self._http_request("GET", f"{base_url}/api/user/state-login",
                                     headers=headers, cookies={'SessionID': session_id},
                                     verify_ssl=verify_ssl)
        
        state_login = xmltodict.parse(response.text)
        if "response" in state_login:
            return {
                "logged_in": int(state_login['response'].get('State', -1)) == 0,
                "password_type": state_login['response'].get('password_type', ''),
                "remain_wait_time": int(state_login['response'].get('remainwaittime', 0))
            }
        return {"logged_in": False, "password_type": "", "remain_wait_time": 0}


class WebUI21Implementation(WebUI17Implementation):
    """
    WebUI version 21 implementation.
    
    This class implements the HiLink API for modems running WebUI version 21.x.
    It inherits most functionality from WebUI17Implementation but with some
    key differences in session initialization and WAN IP retrieval.
    
    Key differences from WebUI 17:
        - Token retrieval similar to WebUI 10
        - WAN IP from device info endpoint (like WebUI 10)
        - Version verification during initialization
    """
    
    def initialize_session(self, base_url: str, session_id: Optional[str], token: Optional[str], verify_ssl: bool = False) -> Tuple[str, str]:
        """Initialize session for WebUI 21"""
        # Get initial session
        response = self._http_request("GET", f"{base_url}/", verify_ssl=verify_ssl)
        
        # Extract session ID from cookies
        new_session_id = response.cookies.get('SessionID', session_id)
        
        # Get token (similar to WebUI 10 but check for version 21)
        response = self._http_request("GET", f"{base_url}/api/webserver/token",
                                     cookies={'SessionID': new_session_id} if new_session_id else None,
                                     verify_ssl=verify_ssl)
        
        token_data = xmltodict.parse(response.text)
        if "response" in token_data and "token" in token_data["response"]:
            login_token = token_data['response']['token']
            new_token = login_token[-32:]  # Last 32 characters
            
            # Verify it's version 21
            response = self._http_request("GET", f"{base_url}/api/device/basic_information",
                                        cookies={'SessionID': new_session_id},
                                        verify_ssl=verify_ssl)
            device_info = xmltodict.parse(response.text)
            if "response" in device_info and "WebUIVersion" in device_info["response"]:
                if "21." in device_info["response"]["WebUIVersion"]:
                    return new_session_id, new_token
        
        raise HiLinkException("WebUI21", "Failed to initialize session")
    
    def get_wan_ip(self, base_url: str, session_id: str, token: str, verify_ssl: bool = False) -> Optional[str]:
        """Get WAN IP for WebUI 21 (uses device info endpoint like WebUI 10)"""
        device_info = self.get_device_info(base_url, session_id, token, verify_ssl)
        return device_info.get("WanIPAddress")


class HiLinkAPI:
    """
    Main HiLink API class for interacting with Huawei HiLink modems.
    
    This is the primary interface for users of the API. It automatically detects
    the WebUI version of the modem and delegates API calls to the appropriate
    version-specific implementation.
    
    The class provides:
        - Automatic WebUI version detection
        - Session management with caching
        - High-level API methods for common operations
        - Error handling and logging
        - TLS/SSL support for secure connections
    
    Attributes:
        modem_name (str): Unique identifier for the modem
        host (str): IP address or hostname of the modem
        username (str): Username for authentication
        password (str): Password for authentication
        logger (logging.Logger): Logger instance for debugging
        use_tls (bool): Whether to use HTTPS
        verify_tls (bool): Whether to verify SSL certificates
        base_url (str): Complete base URL including protocol
        session_id (str): Current session ID
        token (str): Current verification token
        webui_version (int): Detected WebUI version (10, 17, or 21)
        logged_in (bool): Current login status
        login_required (bool): Whether login is required for this modem
        
    Example:
        >>> # Basic usage
        >>> api = HiLinkAPI("MyModem", "192.168.8.1")
        >>> api.initialize()
        >>> info = api.get_device_info()
        
        >>> # With authentication
        >>> api = HiLinkAPI("MyModem", "192.168.8.1", "admin", "password")
        >>> api.initialize()
        >>> if api.check_login_required():
        >>>     api.login()
        >>> api.switch_connection(enable=True)
        
        >>> # With TLS/SSL
        >>> api = HiLinkAPI("MyModem", "192.168.8.1", use_tls=True, verify_tls=True)
        >>> api.initialize()
    """
    
    # Static property for the API implementation (non-final, can be changed)
    api_implementation: Optional[HiLinkAPIInterface] = None
    
    def __init__(self, modem_name: str, host: str, username: Optional[str] = None,
                 password: Optional[str] = None, logger: Optional[logging.Logger] = None,
                 use_tls: bool = False, verify_tls: bool = False):
        """
        Initialize HiLink API
        
        Args:
            modem_name: Unique name for the modem
            host: IP address or hostname of the modem
            username: Username for authentication (optional)
            password: Password for authentication (optional)
            logger: Logger instance (optional)
            use_tls: Use HTTPS instead of HTTP (default: False)
            verify_tls: Verify SSL certificates when using HTTPS (default: False)
        """
        self.modem_name = modem_name
        self.host = host
        self.username = username or ""
        self.password = password or ""
        self.logger = logger or logging.getLogger(__name__)
        self.use_tls = use_tls
        self.verify_tls = verify_tls
        
        # Build base URL with protocol
        self.protocol = "https" if use_tls else "http"
        self.base_url = f"{self.protocol}://{host}"
        
        # Session state
        self.session_id: Optional[str] = None
        self.token: Optional[str] = None
        self.webui_version: Optional[int] = None
        self.logged_in: bool = False
        self.login_required: bool = False
        
        # Device information cache
        self._device_info_cache: Dict[str, Any] = {}
        self._network_info_cache: Dict[str, Any] = {}
        self._connection_status_cache: Dict[str, Any] = {}
        
        # Error tracking
        self.last_error_code: int = 0
        self.last_error_message: str = ""
        
        # Log TLS configuration
        if use_tls:
            self.logger.info(f"Using HTTPS with SSL verification: {verify_tls}")
    
    def initialize(self) -> bool:
        """
        Initialize the API and automatically detect WebUI version.
        
        This method must be called before using any other API methods.
        It attempts to detect the WebUI version by trying each supported
        version in order (10, 21, 17) and stops at the first successful match.
        
        Returns:
            True if initialization successful, False otherwise
            
        Example:
            >>> api = HiLinkAPI("MyModem", "192.168.8.1")
            >>> if api.initialize():
            >>>     print(f"Detected WebUI version: {api.webui_version}")
            >>> else:
            >>>     print("Failed to initialize API")
        """
        try:
            # Try WebUI 10 first
            try:
                self.logger.debug("Trying WebUI version 10...")
                impl = WebUI10Implementation()
                session_id, token = impl.initialize_session(self.base_url, None, None, self.verify_tls)
                self.webui_version = 10
                self.session_id = session_id
                self.token = token
                HiLinkAPI.api_implementation = impl
                self.logger.info(f"Detected WebUI version 10")
                return True
            except:
                pass
            
            # Try WebUI 21
            try:
                self.logger.debug("Trying WebUI version 21...")
                impl = WebUI21Implementation()
                session_id, token = impl.initialize_session(self.base_url, None, None, self.verify_tls)
                self.webui_version = 21
                self.session_id = session_id
                self.token = token
                HiLinkAPI.api_implementation = impl
                self.logger.info(f"Detected WebUI version 21")
                return True
            except:
                pass
            
            # Try WebUI 17
            try:
                self.logger.debug("Trying WebUI version 17...")
                impl = WebUI17Implementation()
                session_id, token = impl.initialize_session(self.base_url, None, None, self.verify_tls)
                self.webui_version = 17
                self.session_id = session_id
                self.token = token
                HiLinkAPI.api_implementation = impl
                self.logger.info(f"Detected WebUI version 17")
                return True
            except:
                pass
            
            raise HiLinkException(self.modem_name, "Failed to detect WebUI version")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize API: {e}")
            return False
    
    def check_login_required(self) -> bool:
        """
        Check if login/authentication is required for API operations.
        
        Some modems or configurations don't require authentication for basic
        operations. This method checks whether login is necessary.
        
        Returns:
            True if login is required, False otherwise
            
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            self.login_required = self.api_implementation.check_login_required(
                self.base_url, self.session_id, self.token, self.verify_tls
            )
            return self.login_required
        except Exception as e:
            self.logger.error(f"Failed to check login requirement: {e}")
            return False
    
    def login(self) -> bool:
        """
        Perform login authentication with the modem.
        
        This method uses the username and password provided during initialization
        to authenticate with the modem. The exact authentication mechanism depends
        on the WebUI version.
        
        Returns:
            True if login successful, False otherwise
            
        Raises:
            HiLinkException: If API not initialized
            
        Note:
            Username and password must be provided during initialization
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        if not self.username or not self.password:
            self.logger.error("Username and password are required for login")
            return False
        
        try:
            # Refresh session/token before login if needed
            self.session_id, self.token = self.api_implementation.initialize_session(
                self.base_url, self.session_id, self.token, self.verify_tls
            )
            
            self.logged_in = self.api_implementation.login(
                self.base_url, self.username, self.password, self.session_id, self.token, self.verify_tls
            )
            
            if self.logged_in:
                self.logger.info("Login successful")
            else:
                self.logger.error("Login failed")
            
            return self.logged_in
            
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def logout(self) -> bool:
        """Perform logout"""
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            result = self.api_implementation.logout(self.base_url, self.session_id, self.token, self.verify_tls)
            if result:
                self.logged_in = False
                self.logger.info("Logout successful")
            return result
        except Exception as e:
            self.logger.error(f"Logout error: {e}")
            return False
    
    def get_device_info(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive device information.
        
        Retrieves detailed information about the modem including model name,
        serial numbers, version information, and capabilities.
        
        Args:
            use_cache: If True, return cached data if available
            
        Returns:
            Dictionary containing device information with keys such as:
                - DeviceName: Model name
                - SerialNumber: Device serial
                - Imei: IMEI number
                - Imsi: IMSI number
                - Iccid: SIM card ICCID
                - HardwareVersion: Hardware version
                - SoftwareVersion: Firmware version
                - WebUIVersion: WebUI version
                
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        if use_cache and self._device_info_cache:
            return self._device_info_cache
        
        try:
            self._device_info_cache = self.api_implementation.get_device_info(
                self.base_url, self.session_id, self.token, self.verify_tls
            )
            if self._device_info_cache.get("WebUIVersion", False):
                if "17." in self._device_info_cache.get("WebUIVersion"):
                    self.api_implementation = WebUI17Implementation()
            return self._device_info_cache
        except Exception as e:
            self.logger.error(f"Failed to get device info: {e}")
            return {}
    
    def get_wan_ip(self) -> Optional[str]:
        """
        Get the current WAN IP address assigned by the carrier.
        
        Returns:
            WAN IP address as string, or None if not connected
            
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            return self.api_implementation.get_wan_ip(self.base_url, self.session_id, self.token, self.verify_tls)
        except Exception as e:
            self.logger.error(f"Failed to get WAN IP: {e}")
            return None
    
    def get_network_info(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get network information"""
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        if use_cache and self._network_info_cache:
            return self._network_info_cache
        
        try:
            self._network_info_cache = self.api_implementation.get_network_info(
                self.base_url, self.session_id, self.token, self.verify_tls
            )
            return self._network_info_cache
        except Exception as e:
            self.logger.error(f"Failed to get network info: {e}")
            return {}
    
    def get_connection_status(self, use_cache: bool = False) -> Dict[str, Any]:
        """Get connection status"""
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        if use_cache and self._connection_status_cache:
            return self._connection_status_cache
        
        try:
            self._connection_status_cache = self.api_implementation.get_connection_status(
                self.base_url, self.session_id, self.token, self.verify_tls
            )
            return self._connection_status_cache
        except Exception as e:
            self.logger.error(f"Failed to get connection status: {e}")
            return {}
    
    def switch_connection(self, enable: bool) -> bool:
        """
        Enable or disable the mobile data connection.
        
        Args:
            enable: True to enable data connection, False to disable
            
        Returns:
            True if operation successful, False otherwise
            
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            result = self.api_implementation.switch_connection(
                self.base_url, self.session_id, self.token, enable, self.verify_tls
            )
            if result:
                self.logger.info(f"Data connection {'enabled' if enable else 'disabled'}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to switch connection: {e}")
            return False
    
    def switch_network_mode(self, mode: str) -> bool:
        """
        Switch the network mode.
        
        Args:
            mode: Network mode to switch to. Valid values:
                - "LTE": 4G LTE only
                - "WCDMA": 3G WCDMA/UMTS only
                - "GSM": 2G GSM only
                - "AUTO": Automatic mode selection
                
        Returns:
            True if mode switch successful, False otherwise
            
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            result = self.api_implementation.switch_network_mode(
                self.base_url, self.session_id, self.token, mode, self.verify_tls
            )
            if result:
                self.logger.info(f"Network mode switched to {mode}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to switch network mode: {e}")
            return False
    
    def configure_data_connection(self, roaming: bool = True, max_idle_time: int = 0) -> bool:
        """
        Configure data connection settings.
        
        Args:
            roaming: Enable or disable data roaming
            max_idle_time: Maximum idle time in seconds (0 = disabled)
            
        Returns:
            True if configuration successful, False otherwise
            
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            result = self.api_implementation.configure_data_connection(
                self.base_url, self.session_id, self.token, roaming, max_idle_time, self.verify_tls
            )
            if result:
                self.logger.info(f"Data connection configured: roaming={roaming}, max_idle={max_idle_time}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to configure data connection: {e}")
            return False
    
    def reboot(self) -> bool:
        """
        Reboot the modem.
        
        This initiates a modem reboot. The connection will be lost and the
        modem will be unavailable for approximately 30-60 seconds.
        
        Returns:
            True if reboot command sent successfully
            
        Raises:
            HiLinkException: If API not initialized
            
        Warning:
            This will disconnect all active connections
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            result = self.api_implementation.reboot(self.base_url, self.session_id, self.token, self.verify_tls)
            if result:
                self.logger.info("Reboot initiated")
            return result
        except Exception as e:
            self.logger.error(f"Failed to reboot: {e}")
            return False
    
    def get_signal_info(self) -> Dict[str, Any]:
        """
        Get signal strength and quality information.
        
        Returns:
            Dictionary containing signal information such as:
                - rssi: Received Signal Strength Indicator
                - rsrp: Reference Signal Received Power (LTE)
                - rsrq: Reference Signal Received Quality (LTE)
                - sinr: Signal to Interference plus Noise Ratio
                - cell_id: Current cell ID
                
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            return self.api_implementation.get_signal_info(self.base_url, self.session_id, self.token, self.verify_tls)
        except Exception as e:
            self.logger.error(f"Failed to get signal info: {e}")
            return {}
    
    def get_sms_count(self) -> Dict[str, int]:
        """
        Get SMS message counts.
        
        Returns:
            Dictionary with SMS counts:
                - unread: Number of unread messages
                - inbox: Total messages in inbox
                - outbox: Total messages in outbox
                - draft: Number of draft messages
                
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            return self.api_implementation.get_sms_count(self.base_url, self.session_id, self.token, self.verify_tls)
        except Exception as e:
            self.logger.error(f"Failed to get SMS count: {e}")
            return {"unread": 0, "inbox": 0, "outbox": 0, "draft": 0}
    
    def get_login_state(self) -> Dict[str, Any]:
        """Get current login state"""
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            return self.api_implementation.get_login_state(self.base_url, self.session_id, self.token, self.verify_tls)
        except Exception as e:
            self.logger.error(f"Failed to get login state: {e}")
            return {"logged_in": False, "password_type": "", "remain_wait_time": 0}
    
    def refresh_session(self) -> bool:
        """
        Refresh the current session and token.
        
        This method can be used to refresh an expired session or to ensure
        the session remains active during long-running operations.
        
        Returns:
            True if refresh successful, False otherwise
            
        Raises:
            HiLinkException: If API not initialized
        """
        if not self.api_implementation:
            raise HiLinkException(self.modem_name, "API not initialized")
        
        try:
            self.session_id, self.token = self.api_implementation.initialize_session(
                self.base_url, self.session_id, self.token, self.verify_tls
            )
            self.logger.debug("Session refreshed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh session: {e}")
            return False
    
    @classmethod
    def set_implementation(cls, version: int) -> None:
        """
        Manually set the API implementation version.
        
        This method allows overriding the automatic version detection.
        Useful for testing or when automatic detection fails.
        
        Args:
            version: WebUI version number (10, 17, or 21)
            
        Raises:
            ValueError: If unsupported version specified
            
        Example:
            >>> HiLinkAPI.set_implementation(17)
            >>> api = HiLinkAPI("MyModem", "192.168.8.1")
        """
        if version == 10:
            cls.api_implementation = WebUI10Implementation()
        elif version == 17:
            cls.api_implementation = WebUI17Implementation()
        elif version == 21:
            cls.api_implementation = WebUI21Implementation()
        else:
            raise ValueError(f"Unsupported WebUI version: {version}")
    
    @classmethod
    def get_implementation(cls) -> Optional[HiLinkAPIInterface]:
        """
        Get the current API implementation instance.
        
        Returns:
            The current HiLinkAPIInterface implementation, or None if not set
            
        Example:
            >>> impl = HiLinkAPI.get_implementation()
            >>> if impl:
            >>>     print(type(impl).__name__)
        """
        return cls.api_implementation