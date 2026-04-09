"""Tests for cloud provider helpers and mappings."""

from __future__ import annotations

import hashlib
import unittest
from unittest.mock import patch

from pydreo.cloud.auth import (
    CloudConfig,
    extract_token_region,
    prepare_cloud_password,
    resolve_cloud_endpoint,
    strip_token_region,
)
from pydreo.cloud.const import BASE_URL, EU_BASE_URL
from pydreo.cloud.provider import CloudProvider
from pydreo.cloud.transport import CloudTransport


class FakeCloudTransport:
    """Fake HTTP transport used by unit tests."""

    def login(self, username, password):
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "access_token": "token-value:EU",
                "endpoint": EU_BASE_URL,
                "username": username,
                "password": password,
            },
        }

    def get_devices(self, endpoint, access_token):
        return {
            "code": 0,
            "msg": "success",
            "data": [
                {
                    "deviceSn": "SN-100",
                    "deviceName": "Living Room Tower Fan",
                    "deviceModel": "DR-HTF001",
                    "online": True,
                }
            ],
        }

    def get_device_state(self, endpoint, access_token, devicesn):
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "deviceSn": devicesn,
                "power": "on",
                "speed": 3,
                "connected": True,
            },
        }

    def set_device_state(self, endpoint, access_token, devicesn, changes):
        return {
            "code": 0,
            "msg": "success",
            "data": {"deviceSn": devicesn, "desired": dict(changes), "accepted": True},
        }


class CloudProviderTests(unittest.TestCase):
    """Cloud provider coverage for token parsing and payload normalization."""

    def test_token_helpers(self) -> None:
        self.assertEqual(extract_token_region("abc:EU"), "EU")
        self.assertEqual(extract_token_region("abc:NA"), "NA")
        self.assertEqual(extract_token_region("abc"), "NA")
        self.assertEqual(strip_token_region("abc:EU"), "abc")
        self.assertEqual(resolve_cloud_endpoint("abc:EU"), EU_BASE_URL)
        self.assertEqual(resolve_cloud_endpoint("abc"), BASE_URL)

    def test_prepare_cloud_password_hashes_plaintext(self) -> None:
        self.assertEqual(
            prepare_cloud_password("secret"),
            hashlib.md5(b"secret").hexdigest(),
        )

    def test_prepare_cloud_password_preserves_md5_digest(self) -> None:
        digest = hashlib.md5(b"secret").hexdigest()

        self.assertEqual(prepare_cloud_password(digest), digest)
        self.assertEqual(prepare_cloud_password(digest.upper()), digest.upper())

    def test_transport_hashes_plaintext_password(self) -> None:
        transport = CloudTransport()

        with patch.object(
            transport,
            "_request",
            return_value={"code": 0, "data": {"access_token": "token-value:EU"}},
        ) as mock_request:
            transport.login("demo@example.com", "secret")

        body = mock_request.call_args.kwargs["json_body"]
        self.assertEqual(body["password"], hashlib.md5(b"secret").hexdigest())

    def test_transport_preserves_prehashed_password(self) -> None:
        transport = CloudTransport()
        digest = hashlib.md5(b"secret").hexdigest()

        with patch.object(
            transport,
            "_request",
            return_value={"code": 0, "data": {"access_token": "token-value:EU"}},
        ) as mock_request:
            transport.login("demo@example.com", digest)

        body = mock_request.call_args.kwargs["json_body"]
        self.assertEqual(body["password"], digest)

    def test_transport_uses_v2_endpoints_and_dreover_param(self) -> None:
        transport = CloudTransport()

        with patch.object(
            transport,
            "_request",
            return_value={"code": 0, "data": {}},
        ) as mock_request:
            transport.get_devices(BASE_URL, "token-value:NA")
            transport.get_device_state(BASE_URL, "token-value:NA", "SN-100")
            transport.set_device_state(BASE_URL, "token-value:NA", "SN-100", {"power": "on"})

        calls = mock_request.call_args_list
        self.assertIn("/api/v2/device/list", calls[0].args[0])
        self.assertEqual(calls[0].kwargs["params"]["dreover"], "1.0.0")
        self.assertIn("/api/v2/device/state", calls[1].args[0])
        self.assertIn("/api/v2/device/control", calls[2].args[0])

    def test_provider_maps_devices_and_state(self) -> None:
        provider = CloudProvider(
            CloudConfig(username="demo@example.com", password="secret"),
            transport=FakeCloudTransport(),
        )

        auth = provider.authenticate()
        devices = provider.discover_devices()
        state = provider.get_device_state("SN-100")
        result = provider.set_device_state("SN-100", power="off")

        self.assertEqual(auth["endpoint"], EU_BASE_URL)
        self.assertEqual(len(devices), 1)
        self.assertEqual(devices[0].identity.serial_number, "SN-100")
        self.assertEqual(devices[0].metadata["token_region"], "EU")
        self.assertEqual(state.properties["speed"], 3)
        self.assertTrue(result.raw["code"] == 0)
        self.assertEqual(result.raw["data"]["desired"]["power"], "off")

    def test_compatibility_client_returns_legacy_shapes(self) -> None:
        provider = CloudProvider(
            CloudConfig(username="demo@example.com", password="secret"),
            transport=FakeCloudTransport(),
        )

        devices = provider.get_legacy_devices()
        state = provider.get_legacy_device_state("SN-100")

        self.assertEqual(devices[0]["deviceSn"], "SN-100")
        self.assertEqual(state["speed"], 3)

    def test_provider_reauthenticates_once_on_auth_failure(self) -> None:
        class ReauthTransport(FakeCloudTransport):
            def __init__(self):
                self.calls = 0

            def get_devices(self, endpoint, access_token):
                self.calls += 1
                if self.calls == 1:
                    from pydreo.core.exceptions import DreoAuthenticationError

                    raise DreoAuthenticationError("expired")
                return super().get_devices(endpoint, access_token)

        transport = ReauthTransport()
        provider = CloudProvider(
            CloudConfig(username="demo@example.com", password="secret"),
            transport=transport,
        )

        devices = provider.discover_devices()

        self.assertEqual(len(devices), 1)
        self.assertEqual(transport.calls, 2)

    def test_provider_is_http_only(self) -> None:
        provider = CloudProvider(
            CloudConfig(username="demo@example.com", password="secret"),
            transport=FakeCloudTransport(),
        )

        self.assertFalse(hasattr(provider, "subscribe"))


if __name__ == "__main__":
    unittest.main()
