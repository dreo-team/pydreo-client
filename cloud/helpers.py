"""
DreoCloud helper utilities.

This module provides helper functions for interacting with the DreoCloud API,
including authentication, device management, and API communication.
"""
from datetime import datetime
from typing import Optional, Dict, Any
import logging

import requests

from .const import BASE_URL, EU_BASE_URL, CLIENT_ID, CLIENT_SECRET, USER_AGENT, REQUEST_TIMEOUT, ENDPOINTS
from . import __version__
from .exceptions import (
    DreoBusinessException,
    DreoException,
    DreoFlowControlException,
)

logger = logging.getLogger(__name__)


class Helpers:
    """Helper class containing static methods for DreoCloud API operations."""

    @staticmethod
    def parse_token_and_get_endpoint(access_token: str) -> str:
        """
        Parse access token to determine the appropriate endpoint based on region suffix.

        Args:
            access_token: The access token which may contain region suffix.

        Returns:
            The appropriate base URL endpoint for the region.
        """
        if not access_token:
            return BASE_URL

        # Check if token has region suffix (format: token:REGION)
        if ":" in access_token:
            token_parts = access_token.split(":")
            if len(token_parts) == 2:
                region = token_parts[1].upper()
                if region == "EU":
                    logger.debug("Using EU endpoint based on token suffix")
                    return EU_BASE_URL
                elif region == "NA":
                    logger.debug("Using US endpoint based on token suffix")
                    return BASE_URL
                else:
                    logger.debug("Unknown region suffix '%s', defaulting to US endpoint", region)
                    return BASE_URL

        # No suffix or unrecognized format, default to US endpoint
        logger.debug("No region suffix found in token, using US endpoint")
        return BASE_URL

    @staticmethod
    def clean_token(access_token: str) -> str:
        """
        Remove region suffix from access token.

        Args:
            access_token: The access token which may contain region suffix.

        Returns:
            Clean access token without region suffix.
        """
        if not access_token:
            return access_token

        # Remove region suffix if present (format: token:REGION)
        if ":" in access_token:
            token_parts = access_token.split(":")
            if len(token_parts) == 2:
                clean_token = token_parts[0]
                logger.debug("Removed region suffix from token")
                return clean_token

        # No suffix found, return original token
        return access_token

    @staticmethod
    def login(username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with DreoCloud API using username and password.

        Args:
            username: User's email address.
            password: User's password.

        Returns:
            Authentication response containing access token and endpoint.

        Raises:
            DreoException: If authentication fails.
        """
        if not username or not password:
            raise DreoException("Username and password are required")

        headers = {
            "Content-Type": "application/json",
            "UA": USER_AGENT
        }
        params = {
            "timestamp": Helpers.timestamp(),
            "pydreover": __version__,
        }
        body = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "openapi",
            "scope": "all",
            "email": username,
            "password": password,
        }

        response = Helpers.call_api(
            BASE_URL + ENDPOINTS["LOGIN"],
            "post",
            headers,
            params,
            body
        )

        # Extract access token and determine endpoint based on token suffix
        access_token = response.get("access_token")
        if access_token:
            endpoint = Helpers.parse_token_and_get_endpoint(access_token)
            response["endpoint"] = endpoint
            logger.debug("Determined endpoint based on token region")

        return response

    @staticmethod
    def devices(endpoint: str, access_token: str) -> Dict[str, Any]:
        """
        Get list of devices associated with the account.

        Args:
            endpoint: API endpoint URL.
            access_token: Authentication access token.

        Returns:
            List of devices.

        Raises:
            DreoException: If API call fails.
        """
        if not endpoint or not access_token:
            raise DreoException("Endpoint and access token are required")

        # Clean token by removing region suffix
        clean_token = Helpers.clean_token(access_token)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_token}",
            "UA": USER_AGENT,
        }
        params = {
            "timestamp": Helpers.timestamp(),
            "pydreover": __version__,
        }

        return Helpers.call_api(
            endpoint + ENDPOINTS["DEVICES"],
            "get",
            headers,
            params
        )

    @staticmethod
    def status(endpoint: str, access_token: str, devicesn: str) -> Dict[str, Any]:
        """
        Get current status of a specific device.

        Args:
            endpoint: API endpoint URL.
            access_token: Authentication access token.
            devicesn: Device serial number.

        Returns:
            Device status information.

        Raises:
            DreoException: If API call fails.
        """
        if not all([endpoint, access_token, devicesn]):
            raise DreoException("Endpoint, access token, and device serial number are required")

        # Clean token by removing region suffix
        clean_token = Helpers.clean_token(access_token)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_token}",
            "UA": USER_AGENT,
        }
        params = {
            "deviceSn": devicesn,
            "timestamp": Helpers.timestamp(),
            "pydreover": __version__,
        }

        return Helpers.call_api(
            endpoint + ENDPOINTS["DEVICE_STATE"],
            "get",
            headers,
            params
        )

    @staticmethod
    def update(endpoint: str, access_token: str, devicesn: str, **kwargs) -> Dict[str, Any]:
        """
        Update device settings.

        Args:
            endpoint: API endpoint URL.
            access_token: Authentication access token.
            devicesn: Device serial number.
            **kwargs: Device parameters to update.

        Returns:
            Update response.

        Raises:
            DreoException: If API call fails.
        """
        if not all([endpoint, access_token, devicesn]):
            raise DreoException("Endpoint, access token, and device serial number are required")

        # Clean token by removing region suffix
        clean_token = Helpers.clean_token(access_token)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {clean_token}",
            "UA": USER_AGENT,
        }
        params = {
            "timestamp": Helpers.timestamp(),
            "pydreover": __version__,
        }

        return Helpers.call_api(
            endpoint + ENDPOINTS["DEVICE_CONTROL"],
            "post",
            headers,
            params,
            Helpers.update_body(devicesn, **kwargs),
        )

    @staticmethod
    def call_api(
        api: str,
        method: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP API calls to DreoCloud endpoints.

        Args:
            api: API endpoint URL.
            method: HTTP method ('get' or 'post').
            headers: HTTP headers.
            params: URL parameters.
            json_body: JSON request body.

        Returns:
            API response data.

        Raises:
            DreoException: For general API errors.
            DreoBusinessException: For business logic errors.
            DreoFlowControlException: For rate limiting errors.
        """
        try:
            response = None
            if method.lower() == "get":
                response = requests.get(
                    api,
                    headers=headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT
                )
            elif method.lower() == "post":
                response = requests.post(
                    api,
                    headers=headers,
                    params=params,
                    json=json_body,
                    timeout=REQUEST_TIMEOUT
                )
            else:
                raise DreoException(f"Unsupported HTTP method: {method}")

        except requests.exceptions.Timeout as exc:
            raise DreoException("Request timed out") from exc
        except requests.exceptions.ConnectionError as exc:
            raise DreoException("Connection error") from exc
        except requests.exceptions.RequestException as e:
            raise DreoException(f"Request failed: {str(e)}") from e

        if response is None:
            raise DreoException("No response received from server")

        return Helpers._handle_response(response)

    @staticmethod
    def _handle_response(response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and extract data.

        Args:
            response: HTTP response object.

        Returns:
            Response data.

        Raises:
            DreoException: For various API errors.
        """
        if response.status_code == 200:
            try:
                response_body = response.json()
                code = response_body.get("code")
                if code == 0:
                    return response_body.get("data", {})
                raise DreoBusinessException(
                    response_body.get("msg", "Unknown business error")
                )
            except ValueError as e:
                raise DreoException(f"Invalid JSON response: {str(e)}") from e

        if response.status_code == 401:
            raise DreoBusinessException("Invalid authentication credentials")
        if response.status_code == 429:
            raise DreoFlowControlException(
                "Request rate limit exceeded. Please try again later."
            )
        if response.status_code >= 500:
            raise DreoException(
                "Server error occurred. Please try again later."
            )
        raise DreoException(
            f"API request failed with status code: {response.status_code}"
        )

    @staticmethod
    def update_body(devicesn: str, **kwargs) -> Dict[str, Any]:
        """
        Create request body for device update operations.

        Args:
            devicesn: Device serial number.
            **kwargs: Device parameters to update.

        Returns:
            Formatted request body.
        """
        return {
            "devicesn": devicesn,
            "desired": dict(kwargs)
        }

    @staticmethod
    def timestamp() -> int:
        """
        Generate current timestamp in milliseconds.

        Returns:
            Current timestamp in milliseconds.
        """
        return int(datetime.now().timestamp() * 1000)
