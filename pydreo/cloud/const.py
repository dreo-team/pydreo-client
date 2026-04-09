"""Constants for the Dreo Cloud provider."""

BASE_URL = "https://open-api-us.dreo-tech.com"
EU_BASE_URL = "https://open-api-eu.dreo-tech.com"
CLIENT_ID = "89ef537b2202481aaaf9077068bcb0c9"
CLIENT_SECRET = "41b20a1f60e9499e89c8646c31f93ea1"
USER_AGENT = "openapi/1.0.0"
REQUEST_TIMEOUT = 8
API_VERSION = "1.0.0"

ENDPOINTS = {
    "LOGIN": "/api/oauth/login",
    "DEVICES": "/api/v2/device/list",
    "DEVICE_STATE": "/api/v2/device/state",
    "DEVICE_CONTROL": "/api/v2/device/control",
}
