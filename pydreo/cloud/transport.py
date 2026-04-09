"""HTTP transport for Dreo Cloud."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional

from ..core.exceptions import (
    DreoAuthenticationError,
    DreoBusinessError,
    DreoConnectionError,
    DreoProviderUnavailableError,
    DreoRateLimitError,
)
from ..version import __version__
from .auth import prepare_cloud_password, resolve_cloud_endpoint, strip_token_region
from .const import (
    API_VERSION,
    BASE_URL,
    CLIENT_ID,
    CLIENT_SECRET,
    ENDPOINTS,
    REQUEST_TIMEOUT,
    USER_AGENT,
)


class CloudTransport:
    """Thin HTTP transport layer used by the cloud provider."""

    def __init__(
        self,
        *,
        session: Optional[Any] = None,
        user_agent: str = USER_AGENT,
        request_timeout: float = REQUEST_TIMEOUT,
    ) -> None:
        self._session = session
        self._user_agent = user_agent
        self._request_timeout = request_timeout

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate and return the cloud auth payload."""
        body = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "openapi",
            "scope": "all",
            "email": username,
            "password": prepare_cloud_password(password),
        }
        payload = self._request(
            BASE_URL + ENDPOINTS["LOGIN"],
            method="post",
            params=self._base_params(),
            json_body=body,
        )
        auth_data = payload.get("data", payload)
        access_token = auth_data.get("access_token") or auth_data.get("token")
        if access_token:
            auth_data["endpoint"] = resolve_cloud_endpoint(access_token)
        return payload

    def get_devices(self, endpoint: str, access_token: str) -> Dict[str, Any]:
        """Call the cloud device list endpoint."""
        return self._request(
            endpoint + ENDPOINTS["DEVICES"],
            method="get",
            access_token=access_token,
            params=self._base_params(),
        )

    def get_device_state(self, endpoint: str, access_token: str, devicesn: str) -> Dict[str, Any]:
        """Call the cloud device state endpoint."""
        params = self._base_params()
        params["deviceSn"] = devicesn
        return self._request(
            endpoint + ENDPOINTS["DEVICE_STATE"],
            method="get",
            access_token=access_token,
            params=params,
        )

    def set_device_state(
        self,
        endpoint: str,
        access_token: str,
        devicesn: str,
        changes: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Call the cloud device control endpoint."""
        return self._request(
            endpoint + ENDPOINTS["DEVICE_CONTROL"],
            method="post",
            access_token=access_token,
            params=self._base_params(),
            json_body={"devicesn": devicesn, "desired": dict(changes)},
        )

    def _request(
        self,
        url: str,
        *,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json", "UA": self._user_agent}
        if access_token:
            clean_token = strip_token_region(access_token)
            headers["Authorization"] = "Bearer {token}".format(token=clean_token)

        requests = self._requests_module()
        session = self._get_session()
        try:
            response = session.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=self._request_timeout,
            )
        except requests.exceptions.Timeout as err:
            raise DreoConnectionError("Request timed out") from err
        except requests.exceptions.ConnectionError as err:
            raise DreoConnectionError("Connection error") from err
        except requests.exceptions.RequestException as err:
            raise DreoConnectionError("Request failed: {error}".format(error=err)) from err

        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: Any) -> Dict[str, Any]:
        if response.status_code == 200:
            try:
                payload = response.json()
            except ValueError as err:
                raise DreoConnectionError("Cloud response returned invalid JSON") from err
            if isinstance(payload, Mapping) and payload.get("code") == 0:
                return dict(payload)
            if isinstance(payload, Mapping):
                raise DreoBusinessError(payload.get("msg", "Unknown business error"))
            raise DreoBusinessError("Unknown business error")

        if response.status_code in (401, 403):
            raise DreoAuthenticationError("Invalid authentication credentials")
        if response.status_code == 429:
            raise DreoRateLimitError("Request rate limit exceeded")
        if response.status_code >= 500:
            raise DreoConnectionError("Cloud server error occurred")
        raise DreoConnectionError(
            "Cloud request failed with status code: {status}".format(status=response.status_code)
        )

    @staticmethod
    def _base_params() -> Dict[str, Any]:
        return {
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
            "dreover": API_VERSION or __version__,
        }

    def _get_session(self) -> Any:
        if self._session is None:
            self._session = self._requests_module().Session()
        return self._session

    @staticmethod
    def _requests_module() -> Any:
        try:
            import requests  # type: ignore
        except ImportError as err:  # pragma: no cover - depends on runtime environment
            raise DreoProviderUnavailableError(
                "The cloud provider requires the 'requests' package to be installed"
            ) from err
        return requests
