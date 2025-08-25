"""
DreoCloud client module for interacting with the DreoCloud API.

This module provides a Client class for authentication and device management.
"""
import logging
from typing import Optional, Dict, Any

from .helpers import Helpers
from .exceptions import DreoException

logger = logging.getLogger(__name__)


class DreoClient:
    """
    DreoCloud API client for device management.

    This class handles authentication and provides methods for interacting
    with DreoCloud devices.

    Attributes:
        username: Username for authentication.
        password: Password for authentication.
        endpoint: API endpoint URL after authentication.
        access_token: Access token after authentication.
    """

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Initialize the DreoCloud client.

        Args:
            username: Username for authentication (can be set later).
            password: Password for authentication (can be set later).
        """
        super().__init__()
        self.username = username
        self.password = password
        self.endpoint: Optional[str] = None
        self.access_token: Optional[str] = None
        self._authenticated = False

    def login(self) -> Dict[str, Any]:
        """
        Authenticate with the DreoCloud API.

        Returns:
            Authentication response containing endpoint and access token.

        Raises:
            DreoException: If authentication fails or credentials are missing.
        """
        if not self.username or not self.password:
            raise DreoException("Username and password must be set before login")

        try:
            response = Helpers.login(self.username, self.password)
            self.endpoint = response.get("endpoint")
            self.access_token = response.get("access_token")

            if not self.endpoint or not self.access_token:
                raise DreoException("Invalid authentication response")

            self._authenticated = True
            logger.info("Successfully authenticated with DreoCloud API")
            return response

        except Exception as e:
            logger.error("Authentication failed: %s", str(e))
            self._authenticated = False
            raise

    def _get_region_from_token(self) -> str:
        """
        Get region from access token suffix.

        Returns:
            Region string (US, EU, or NA).
        """
        if not self.access_token:
            return "Unknown"

        if ":" in self.access_token:
            token_parts = self.access_token.split(":")
            if len(token_parts) == 2:
                return token_parts[1].upper()

        return "US"  # Default to US if no suffix

    def get_devices(self) -> Dict[str, Any]:
        """
        Get list of available devices.

        Returns:
            List of devices associated with the account.

        Raises:
            DreoException: If not authenticated or API call fails.
        """
        self._ensure_authenticated()

        assert self.endpoint is not None
        assert self.access_token is not None

        try:
            return Helpers.devices(self.endpoint, self.access_token)
        except Exception as e:
            logger.error("Failed to get devices: %s", str(e))
            raise

    def get_status(self, devicesn: str) -> Dict[str, Any]:
        """
        Get device status.

        Args:
            devicesn: Device serial number.

        Returns:
            Device status information.

        Raises:
            DreoException: If not authenticated, device serial is invalid, or API call fails.
        """
        if not devicesn:
            raise DreoException("Device serial number is required")

        self._ensure_authenticated()
        assert self.endpoint is not None
        assert self.access_token is not None

        try:
            status = Helpers.status(self.endpoint, self.access_token, devicesn)
            logger.debug("Retrieved status for device %s", devicesn)
            return status
        except Exception as e:
            logger.error("Failed to get status for device %s: %s", devicesn, str(e))
            raise

    def update_status(self, devicesn: str, **kwargs) -> Dict[str, Any]:
        """
        Update device status.

        Args:
            devicesn: Device serial number.
            **kwargs: Device parameters to update.

        Returns:
            Update response.

        Raises:
            DreoException: If not authenticated, device serial is invalid, or API call fails.
        """
        if not devicesn:
            raise DreoException("Device serial number is required")

        if not kwargs:
            raise DreoException("At least one parameter must be specified for update")

        self._ensure_authenticated()
        assert self.endpoint is not None
        assert self.access_token is not None

        try:
            response = Helpers.update(self.endpoint, self.access_token, devicesn, **kwargs)
            logger.debug("Updated device %s with parameters: %s", devicesn, kwargs)
            return response
        except Exception as e:
            logger.error("Failed to update device %s: %s", devicesn, str(e))
            raise

    def _ensure_authenticated(self) -> None:
        """
        Ensure the client is authenticated.

        Raises:
            DreoException: If not authenticated.
        """
        if not self._authenticated or not self.endpoint or not self.access_token:
            raise DreoException("Client must be authenticated. Call login() first.")

    @property
    def is_authenticated(self) -> bool:
        """
        Check if the client is authenticated.

        Returns:
            True if authenticated, False otherwise.
        """
        return self._authenticated and bool(self.endpoint) and bool(self.access_token)
