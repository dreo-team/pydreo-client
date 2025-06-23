"""
HSCloud helper utilities.

This module provides helper functions for interacting with the HSCloud API,
including authentication, device management, and API communication.
"""
from datetime import datetime
from typing import Optional

import requests

from dreo.cloudexception import (
    DreoCloudBusinessException,
    DreoCloudException,
    DreoCloudFlowControlException,
)


class Helpers:
    """Helper class containing static methods for HSCloud API operations."""

    @staticmethod
    def login(username=None, password=None):
        """
        Authenticate with HSCloud API using username and password.
        
        Args:
            username (str, optional): User's email address.
            password (str, optional): User's password.
            
        Returns:
            dict: Authentication response containing access token and endpoint.
        """
        base_url = "https://open-api-us.dreo-cloud.com"

        headers = {"Content-Type": "application/json", "UA": "openapi/1.0.0"}

        params = {"timestamp": Helpers.timestamp()}

        body = {
            "client_id": "89ef537b2202481aaaf9077068bcb0c9",
            "client_secret": "41b20a1f60e9499e89c8646c31f93ea1",
            "grant_type": "openapi",
            "scope": "all",
            "email": username,
            "password": password,
        }

        return Helpers.call_api(
            base_url + "/api/oauth/login", "post", headers, params, body
        )

    @staticmethod
    def devices(endpoint=None, access_token=None):
        """
        Get list of devices associated with the account.
        
        Args:
            endpoint (str, optional): API endpoint URL.
            access_token (str, optional): Authentication access token.
            
        Returns:
            dict: List of devices.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "UA": "openapi/1.0.0",
        }

        params = {"timestamp": Helpers.timestamp()}

        return Helpers.call_api(endpoint + "/api/device/list", "get", headers, params)

    @staticmethod
    def status(endpoint=None, access_token=None, devicesn=None):
        """
        Get current status of a specific device.
        
        Args:
            endpoint (str, optional): API endpoint URL.
            access_token (str, optional): Authentication access token.
            devicesn (str, optional): Device serial number.
            
        Returns:
            dict: Device status information.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "UA": "openapi/1.0.0",
        }

        params = {"deviceSn": devicesn, "timestamp": Helpers.timestamp()}

        return Helpers.call_api(endpoint + "/api/device/state", "get", headers, params)

    @staticmethod
    def update(endpoint=None, access_token=None, devicesn=None, **kwargs):
        """
        Update device settings.
        
        Args:
            endpoint (str, optional): API endpoint URL.
            access_token (str, optional): Authentication access token.
            devicesn (str, optional): Device serial number.
            **kwargs: Device parameters to update.
            
        Returns:
            dict: Update response.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "UA": "openapi/1.0.0",
        }

        params = {"timestamp": Helpers.timestamp()}

        return Helpers.call_api(
            endpoint + "/api/device/control",
            "post",
            headers,
            params,
            Helpers.update_body(devicesn, **kwargs),
        )

    @staticmethod
    def call_api(
        api: str,
        method: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> tuple:
        """
        Make HTTP API calls to DreoCloud endpoints.   
        
        Args:
            api (str): API endpoint URL.
            method (str): HTTP method ('get' or 'post').
            headers (dict, optional): HTTP headers.
            params (dict, optional): URL parameters.
            json_body (dict, optional): JSON request body.
            
        Returns:
            tuple: API response data.
            
        Raises:
            DreoCloudException: For general API errors.
            DreoCloudBusinessException: For business logic errors.
            DreoCloudFlowControlException: For rate limiting errors.
        """
        result = None
        response = None
        try:
            if method.lower() == "get":
                response = requests.get(api, headers=headers, params=params, timeout=8)
            elif method.lower() == "post":
                response = requests.post(
                    api, headers=headers, params=params, json=json_body, timeout=8
                )
        except requests.exceptions.RequestException as e:
            raise DreoCloudException(e) from e

        if response is not None:
            if response.status_code == 200:
                response_body = response.json()
                code = response_body.get("code")
                if code == 0:
                    result = response_body.get("data")
                else:
                    raise DreoCloudBusinessException(response_body.get("msg"))
            elif response.status_code == 401:
                raise DreoCloudBusinessException("invalid auth")
            elif response.status_code == 429:
                raise DreoCloudFlowControlException(
                    "Your request is too frequent, please try again later."
                )
            else:
                raise DreoCloudException(
                    "There is a service problem, please try again later."
                )
        else:
            raise DreoCloudException("No response received from server")

        return result

    @staticmethod
    def update_body(devicesn, **kwargs):
        """
        Create request body for device update operations.
        
        Args:
            devicesn (str): Device serial number.
            **kwargs: Device parameters to update.
            
        Returns:
            dict: Formatted request body.
        """
        data = {"devicesn": devicesn}

        desired = {}
        for key, value in kwargs.items():
            desired.update({key: value})

        data.update({"desired": desired})
        return data

    @staticmethod
    def timestamp():
        """
        Generate current timestamp in milliseconds.
        
        Returns:
            int: Current timestamp in milliseconds.
        """
        return int(datetime.now().timestamp() * 1000)
