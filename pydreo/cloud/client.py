"""Cloud-only compatibility client."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..client import DreoClient as UnifiedDreoClient
from ..core.strategy import ConnectionStrategy
from .auth import CloudConfig, extract_token_region
from .provider import CloudProvider


class DreoCloudClient(UnifiedDreoClient):
    """Compatibility client that preserves the old cloud-only interface."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        *,
        access_token: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        self._cloud_provider = CloudProvider(
            CloudConfig(
                username=username,
                password=password,
                access_token=access_token,
                endpoint=endpoint,
            )
        )
        super().__init__(
            providers=[self._cloud_provider],
            strategy=ConnectionStrategy.CLOUD_ONLY,
        )

    @property
    def username(self) -> Optional[str]:
        return self._cloud_provider.config.username

    @username.setter
    def username(self, value: Optional[str]) -> None:
        self._cloud_provider.config.username = value

    @property
    def password(self) -> Optional[str]:
        return self._cloud_provider.config.password

    @password.setter
    def password(self, value: Optional[str]) -> None:
        self._cloud_provider.config.password = value

    @property
    def endpoint(self) -> Optional[str]:
        return self._cloud_provider.endpoint

    @property
    def access_token(self) -> Optional[str]:
        return self._cloud_provider.access_token

    def _get_region_from_token(self) -> str:
        """Compatibility helper preserved from the original client."""
        return extract_token_region(self.access_token)

    def login(self) -> Dict[str, Any]:
        """Authenticate against Dreo Cloud."""
        return self._cloud_provider.authenticate()

    def get_devices(self) -> List[Dict[str, Any]]:
        """Return raw cloud device entries for compatibility callers."""
        return self._cloud_provider.get_legacy_devices()

    def get_status(self, devicesn: str) -> Dict[str, Any]:
        """Return the raw cloud device state mapping."""
        return self._cloud_provider.get_legacy_device_state(devicesn)

    def update_status(self, devicesn: str, **kwargs: Any) -> Dict[str, Any]:
        """Return the raw cloud control payload."""
        return self._cloud_provider.update_raw_device_state(devicesn, **kwargs)


# Preserve the old import path: from pydreo.cloud.client import DreoClient
DreoClient = DreoCloudClient
