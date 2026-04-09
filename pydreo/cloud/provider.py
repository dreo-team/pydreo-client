"""Cloud provider implementation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional

from ..core.exceptions import (
    DreoAuthenticationError,
    DreoConfigurationError,
    DreoDeviceNotFoundError,
)
from ..core.models import (
    CommandResult,
    DeviceIdentity,
    DeviceInfo,
    DeviceReference,
    DeviceState,
    ProviderKind,
    as_dict,
    mapping_copy,
    maybe_online,
)
from ..core.provider import BaseProvider
from .auth import CloudConfig, extract_token_region, resolve_cloud_endpoint
from .transport import CloudTransport


class CloudProvider(BaseProvider):
    """Provider implementation backed by Dreo Cloud HTTP APIs."""

    kind = ProviderKind.CLOUD

    def __init__(
        self,
        config: Optional[CloudConfig] = None,
        *,
        transport: Optional[CloudTransport] = None,
        name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name)
        self.config = config or CloudConfig()
        self._transport = transport or CloudTransport(
            user_agent=self.config.user_agent,
            request_timeout=self.config.request_timeout,
        )
        self._authenticated = bool(self.config.access_token)
        if self.config.access_token and not self.config.endpoint:
            self.config.endpoint = resolve_cloud_endpoint(self.config.access_token)

    @property
    def endpoint(self) -> Optional[str]:
        return self.config.resolved_endpoint()

    @property
    def access_token(self) -> Optional[str]:
        return self.config.access_token

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated and bool(self.access_token) and bool(self.endpoint)

    def authenticate(self) -> Dict[str, Any]:
        """Authenticate with the cloud or finalize token-based configuration."""
        if self.config.access_token:
            self.config.endpoint = self.config.resolved_endpoint()
            self._authenticated = True
            return {
                "access_token": self.config.access_token,
                "endpoint": self.config.endpoint,
            }

        if not self.config.username or not self.config.password:
            raise DreoAuthenticationError("Cloud username and password are required")

        response = self._transport.login(self.config.username, self.config.password)
        auth_data = self._extract_response_data(response)
        if not isinstance(auth_data, Mapping):
            raise DreoAuthenticationError("Cloud login returned an invalid payload")

        self.config.access_token = auth_data.get("access_token") or auth_data.get("token")
        self.config.endpoint = auth_data.get("endpoint") or resolve_cloud_endpoint(
            self.config.access_token
        )
        self._authenticated = True
        return dict(auth_data)

    def discover_devices(self) -> List[DeviceInfo]:
        """Return normalized device discovery results."""
        payload = self.get_raw_devices()
        return [self._map_device_info(item) for item in self._extract_device_items(payload)]

    def get_device_state(self, device: DeviceReference) -> DeviceState:
        """Return a normalized device state."""
        devicesn = self._resolve_device_serial(device)
        payload = self.get_raw_device_state(devicesn)
        state_payload = self._extract_state_payload(payload)
        identity = self._identity_from_mapping(state_payload, serial_hint=devicesn)
        return DeviceState(
            identity=identity,
            properties=self._extract_properties(state_payload),
            source=self.kind,
            online=self._extract_online(state_payload),
            timestamp=datetime.now(timezone.utc),
            raw=mapping_copy(state_payload),
        )

    def set_device_state(self, device: DeviceReference, **changes: Any) -> CommandResult:
        """Send a control command and normalize the response."""
        devicesn = self._resolve_device_serial(device)
        payload = self.update_raw_device_state(devicesn, **changes)
        identity = self._identity_from_mapping(
            self._extract_state_payload(payload), serial_hint=devicesn
        )
        return CommandResult(
            identity=identity,
            source=self.kind,
            accepted=True,
            changes=dict(changes),
            raw=mapping_copy(payload),
        )

    def get_raw_devices(self) -> Dict[str, Any]:
        """Return the raw cloud discovery payload."""
        def _call() -> Dict[str, Any]:
            assert self.endpoint is not None
            assert self.access_token is not None
            return self._transport.get_devices(self.endpoint, self.access_token)

        return self._request_with_reauth(_call)

    def get_raw_device_state(self, devicesn: str) -> Dict[str, Any]:
        """Return the raw cloud state payload."""
        def _call() -> Dict[str, Any]:
            assert self.endpoint is not None
            assert self.access_token is not None
            return self._transport.get_device_state(
                self.endpoint, self.access_token, devicesn
            )

        return self._request_with_reauth(_call)

    def update_raw_device_state(self, devicesn: str, **changes: Any) -> Dict[str, Any]:
        """Return the raw cloud control payload."""
        if not changes:
            raise DreoConfigurationError("At least one device change must be provided")
        def _call() -> Dict[str, Any]:
            assert self.endpoint is not None
            assert self.access_token is not None
            return self._transport.set_device_state(
                self.endpoint, self.access_token, devicesn, changes
            )

        return self._request_with_reauth(_call)

    def get_legacy_devices(self) -> List[Dict[str, Any]]:
        """Return raw device entries for compatibility callers."""
        return [dict(item) for item in self._extract_device_items(self.get_raw_devices())]

    def get_legacy_device_state(self, devicesn: str) -> Dict[str, Any]:
        """Return the raw device state mapping for compatibility callers."""
        return self._extract_state_payload(self.get_raw_device_state(devicesn))

    def _ensure_authenticated(self) -> None:
        if not self.is_authenticated:
            self.authenticate()

    def _request_with_reauth(self, request: Any) -> Dict[str, Any]:
        """Execute a cloud request and retry once after reauthentication."""
        self._ensure_authenticated()
        try:
            return request()
        except DreoAuthenticationError:
            if not self.config.username or not self.config.password:
                raise
            self._authenticated = False
            self.config.access_token = None
            self.config.endpoint = None
            self.authenticate()
            return request()

    def _resolve_device_serial(self, device: DeviceReference) -> str:
        if isinstance(device, DeviceIdentity):
            if device.serial_number:
                return device.serial_number
            raise DreoDeviceNotFoundError("Cloud operations require a device serial number")
        if not device:
            raise DreoDeviceNotFoundError("Device serial number is required")
        return device

    def _extract_device_items(self, payload: Mapping[str, Any]) -> Iterable[Mapping[str, Any]]:
        raw_items = self._extract_response_data(payload)
        if isinstance(raw_items, list):
            return [as_dict(item) for item in raw_items]

        if isinstance(raw_items, Mapping):
            for key in ("devices", "deviceList", "list", "items", "records"):
                value = raw_items.get(key)
                if isinstance(value, list):
                    return [as_dict(item) for item in value]

        return []

    @staticmethod
    def _extract_response_data(payload: Mapping[str, Any]) -> Any:
        """Return the inner response payload when using the v2 API envelope."""
        if isinstance(payload, Mapping) and "data" in payload:
            return payload["data"]
        return payload

    def _extract_state_payload(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Return the raw device state mapping from a v2 response."""
        state = self._extract_response_data(payload)
        if isinstance(state, Mapping):
            return dict(state)
        return {}

    def _map_device_info(self, item: Mapping[str, Any]) -> DeviceInfo:
        identity = self._identity_from_mapping(item)
        return DeviceInfo(
            identity=identity,
            name=self._first_value(item, "deviceName", "name", "nickname", "alias"),
            model=self._first_value(item, "model", "deviceModel", "productName"),
            category=self._first_value(item, "type", "category", "deviceType"),
            online=self._extract_online(item),
            sources=(self.kind.value,),
            metadata={
                "cloud_endpoint": self.endpoint,
                "token_region": self._token_region(),
            },
            provider_payloads={self.kind.value: dict(item)},
        )

    def _extract_properties(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        for key in ("state", "status", "properties", "reported", "desired"):
            value = payload.get(key)
            if isinstance(value, Mapping):
                return dict(value)
        return dict(payload)

    def _extract_online(self, payload: Mapping[str, Any]) -> Optional[bool]:
        for key in ("online", "isOnline", "available", "status", "connected"):
            if key in payload:
                online = maybe_online(payload.get(key))
                if online is not None:
                    return online
        return None

    def _identity_from_mapping(
        self,
        payload: Mapping[str, Any],
        *,
        serial_hint: Optional[str] = None,
    ) -> DeviceIdentity:
        serial_number = serial_hint or self._first_value(
            payload,
            "deviceSn",
            "devicesn",
            "serialNumber",
            "serial_number",
            "sn",
        )
        return DeviceIdentity(
            serial_number=serial_number,
            device_id=self._first_value(payload, "deviceId", "device_id", "id"),
            product_id=self._first_value(payload, "productId", "product_id", "productType", "sku"),
            mac_address=self._first_value(payload, "mac", "macAddress", "mac_address"),
            ip_address=self._first_value(payload, "ip", "ipAddress", "ip_address"),
            display_name=self._first_value(payload, "deviceName", "name", "nickname"),
        )

    @staticmethod
    def _first_value(payload: Mapping[str, Any], *keys: str) -> Optional[str]:
        for key in keys:
            value = payload.get(key)
            if value not in (None, ""):
                return str(value)
        return None

    def _token_region(self) -> str:
        return extract_token_region(self.config.access_token)
