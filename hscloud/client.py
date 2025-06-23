"""
HSCloud client module for interacting with the HSCloud API.

This module provides a Client class for authentication and device management.
"""
import logging

from .helpers import Helpers

logger = logging.getLogger(__name__)


class Client:
    """
    HSCloud API client for device management.
    
    This class handles authentication and provides methods for interacting
    with HSCloud devices.
    """
    def __init__(self, username=None, password=None):
        """
        Initialize the HSCloud client.
        
        Args:
            username (str, optional): Username for authentication.
            password (str, optional): Password for authentication.
        """
        super().__init__()
        self.username = username
        self.password = password
        self.endpoint = None
        self.access_token = None

    def login(self):
        """
        Authenticate with the HSCloud API.
        
        Returns:
            dict: Authentication response containing endpoint and access token.
        """
        response = Helpers.login(self.username, self.password)
        self.endpoint = response.get("endpoint")
        self.access_token = response.get("access_token")
        return response

    def get_devices(self):
        """
        Get list of available devices.
        
        Returns:
            dict: List of devices associated with the account.
        """
        return Helpers.devices(self.endpoint, self.access_token)

    def get_status(self, devicesn):
        """
        Get device status.
        
        Args:
            devicesn (str): Device serial number.
            
        Returns:
            dict: Device status information.
        """
        return Helpers.status(self.endpoint, self.access_token, devicesn)

    def update_status(self, devicesn, **kwargs):
        """
        Update device status.
        
        Args:
            devicesn (str): Device serial number.
            **kwargs: Device parameters to update.
            
        Returns:
            dict: Update response.
        """
        return Helpers.update(self.endpoint, self.access_token, devicesn, **kwargs)
