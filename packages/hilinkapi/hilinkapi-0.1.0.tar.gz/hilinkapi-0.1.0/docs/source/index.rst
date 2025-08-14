.. HiLink API documentation master file

Welcome to HiLink API's documentation!
=======================================

.. image:: https://img.shields.io/pypi/v/hilinkapi.svg
   :target: https://pypi.org/project/hilinkapi/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/hilinkapi.svg
   :target: https://pypi.org/project/hilinkapi/
   :alt: Python Versions

.. image:: https://img.shields.io/github/license/yourusername/hilinkapi.svg
   :target: https://github.com/yourusername/hilinkapi/blob/main/LICENSE
   :alt: License

Modern Python API for Huawei HiLink modems
-------------------------------------------

HiLink API is a comprehensive Python library for interacting with Huawei HiLink modems. 
It provides automatic WebUI version detection, support for multiple WebUI versions (10, 17, and 21), 
and a clean, well-documented API.

Features
--------

* **Automatic WebUI version detection** - No need to manually specify the modem version
* **Support for WebUI versions 10, 17, and 21** - Works with most Huawei HiLink modems
* **TLS/SSL support** - Secure connections when supported by the modem
* **Comprehensive API** - Device info, network management, SMS monitoring, and more
* **Session management** - Automatic token refresh and session handling
* **Well-documented** - Extensive docstrings and type hints
* **Error handling** - Detailed error messages and exception handling

Installation
------------

Install from PyPI::

    pip install hilinkapi

Or install from source::

    git clone https://github.com/yourusername/hilinkapi.git
    cd hilinkapi
    pip install -e .

Quick Start
-----------

Basic usage example:

.. code-block:: python

    from HiLinkAPI import HiLinkAPI

    # Initialize API
    api = HiLinkAPI("MyModem", "192.168.8.1")
    api.initialize()

    # Get device information
    device_info = api.get_device_info()
    print(f"Device: {device_info.get('DeviceName')}")
    print(f"Serial: {device_info.get('SerialNumber')}")

    # Check WAN IP
    wan_ip = api.get_wan_ip()
    print(f"WAN IP: {wan_ip}")

With authentication:

.. code-block:: python

    from HiLinkAPI import HiLinkAPI

    # Initialize with credentials
    api = HiLinkAPI("MyModem", "192.168.8.1", "admin", "password")
    api.initialize()

    # Login if required
    if api.check_login_required():
        if api.login():
            print("Login successful")
        else:
            print("Login failed")

    # Control data connection
    api.switch_connection(enable=True)

    # Switch network mode
    api.switch_network_mode("LTE")

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   examples
   migration
   changelog

API Reference
=============

.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   api/main
   api/interfaces
   api/implementations
   api/exceptions

Main API Class
--------------

.. automodule:: HiLinkAPI
   :members:
   :undoc-members:
   :show-inheritance:

HiLinkAPI Class
~~~~~~~~~~~~~~~

.. autoclass:: HiLinkAPI.HiLinkAPI
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Exceptions
----------

.. autoclass:: HiLinkAPI.HiLinkException
   :members:
   :undoc-members:
   :show-inheritance:

Interface Classes
-----------------

.. autoclass:: HiLinkAPI.HiLinkAPIInterface
   :members:
   :undoc-members:
   :show-inheritance:

Implementation Classes
----------------------

WebUI10Implementation
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: HiLinkAPI.WebUI10Implementation
   :members:
   :undoc-members:
   :show-inheritance:

WebUI17Implementation
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: HiLinkAPI.WebUI17Implementation
   :members:
   :undoc-members:
   :show-inheritance:

WebUI21Implementation
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: HiLinkAPI.WebUI21Implementation
   :members:
   :undoc-members:
   :show-inheritance:

Examples
========

Basic Connection Management
---------------------------

.. code-block:: python

    from HiLinkAPI import HiLinkAPI
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Initialize API
    api = HiLinkAPI("MyModem", "192.168.8.1", logger=logging.getLogger())
    
    if api.initialize():
        print(f"Connected to WebUI version {api.webui_version}")
        
        # Get signal info
        signal = api.get_signal_info()
        print(f"Signal strength: {signal.get('rssi')} dBm")
        
        # Get network info
        network = api.get_network_info()
        print(f"Network: {network.get('FullName')}")

Network Mode Switching
----------------------

.. code-block:: python

    # Switch between network modes
    api.switch_network_mode("LTE")    # 4G only
    api.switch_network_mode("WCDMA")  # 3G only
    api.switch_network_mode("AUTO")   # Automatic

Data Connection Configuration
-----------------------------

.. code-block:: python

    # Configure data connection
    api.configure_data_connection(
        roaming=True,      # Enable roaming
        max_idle_time=600  # 10 minutes idle timeout
    )

TLS/SSL Support
---------------

.. code-block:: python

    # Use HTTPS with SSL verification
    api = HiLinkAPI(
        "SecureModem", 
        "192.168.8.1",
        use_tls=True,
        verify_tls=True
    )
    api.initialize()

Migration Guide
===============

Migrating from the old API
--------------------------

If you're migrating from the old HiLinkAPI (version 1.x), here are the main changes:

1. **Import changes**: The main class is now imported directly::

    # Old
    from HiLinkAPI import webui
    
    # New
    from HiLinkAPI import HiLinkAPI

2. **Initialization**: The new API uses a simpler initialization::

    # Old
    modem = webui("MyModem", "192.168.8.1", "admin", "password")
    modem.start()
    
    # New
    api = HiLinkAPI("MyModem", "192.168.8.1", "admin", "password")
    api.initialize()

3. **Method names**: Many methods have been renamed for clarity::

    # Old
    modem.queryWANIP()
    
    # New
    api.get_wan_ip()

4. **No threading**: The new API doesn't use background threads by default

5. **Better error handling**: Exceptions now provide more context

See the full migration guide in MIGRATION_GUIDE.md for detailed information.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
