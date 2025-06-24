"""Constants for Dreo Component."""

# API Configuration
BASE_URL = "https://open-api-us.dreo-tech.com"
CLIENT_ID = "89ef537b2202481aaaf9077068bcb0c9"
CLIENT_SECRET = "41b20a1f60e9499e89c8646c31f93ea1"
USER_AGENT = "openapi/1.0.0"
REQUEST_TIMEOUT = 8

# API Endpoints
ENDPOINTS = {
    "LOGIN": "/api/oauth/login",
    "DEVICES": "/api/device/list",
    "DEVICE_STATE": "/api/device/state",
    "DEVICE_CONTROL": "/api/device/control"
}

# device type
DEVICE_TYPE = {
    "DR-HTF001S": "fan",
    "DR-HTF002S": "fan",
    "DR-HTF004S": "fan",
    "DR-HTF005S": "fan",
    "DR-HTF005S-2": "fan",
    "DR-HTF007S": "fan",
    "DR-HTF008S": "fan",
    "DR-HTF009S": "fan",
    "DR-HTF010S": "fan"
}

# fan
FAN_DEVICE = {
    "type": "fan",
    "config": {
        # Tower Fans
        "DR-HTF001S": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 6)
        },
        "DR-HTF002S": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 6)
        },
        "DR-HTF004S": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 12)
        },
        "DR-HTF005S": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 9)
        },
        "DR-HTF005S-2": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 12)
        },
        "DR-HTF007S": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 4)
        },
        "DR-HTF008S": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 5)
        },
        "DR-HTF009S": {
            "preset_modes": ["Sleep", "Auto", "Natural", "Normal"],
            "speed_range": (1, 9)
        },
        "DR-HTF010S": {
            "preset_modes": ["Sleep", "Auto", "Normal"],
            "speed_range": (1, 12)
        }
    }
}
