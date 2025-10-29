"""
Minimal WebSocket client for Dreo Cloud.

Provides basic connect (login via query params), message handling hooks,
and disconnect. Region selection is derived from the access token suffix
using existing helpers.
"""

from __future__ import annotations

import logging
import threading
from typing import Callable, Optional
import importlib

from .const import WS_BASE_URL, ENDPOINTS, USER_AGENT, EU_BASE_URL
from .helpers import Helpers


class DreoWebSocketClient:
    """Basic WebSocket client for Dreo Cloud.

    Usage:
        ws_client = DreoWebSocketClient(access_token)
        ws_client.connect(on_message=print)
        ...
        ws_client.disconnect()
    """

    def __init__(self, access_token: str, logger: Optional[logging.Logger] = None) -> None:
        self.access_token: str = access_token
        self._ws: Optional[object] = None
        self._thread: Optional[threading.Thread] = None
        self._logger = logger or logging.getLogger(__name__)
        self._connected: bool = False

        # Optional user callbacks
        self._user_on_message: Optional[Callable[[str], None]] = None
        self._user_on_error: Optional[Callable[[Exception], None]] = None
        self._user_on_close: Optional[Callable[[Optional[int], Optional[str]], None]] = None
        self._user_on_open: Optional[Callable[[], None]] = None

    # --------------------------- public API ---------------------------
    def connect(
        self,
        *,
        on_message: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_close: Optional[Callable[[Optional[int], Optional[str]], None]] = None,
        on_open: Optional[Callable[[], None]] = None,
        run_forever_kwargs: Optional[dict] = None,
    ) -> None:
        """Open the WebSocket connection and start background loop.

        This performs login via query parameters (accessToken, timestamp).
        """
        self._user_on_message = on_message
        self._user_on_error = on_error
        self._user_on_close = on_close
        self._user_on_open = on_open

        url = self._build_ws_url()
        headers = [f"UA: {USER_AGENT}"]

        self._logger.debug("Connecting WebSocket to %s", url)
        ws_module = importlib.import_module("websocket")  # websocket-client
        self._ws = ws_module.WebSocketApp(
            url,
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self._thread = threading.Thread(
            target=self._ws.run_forever,
            kwargs=run_forever_kwargs or {},
            daemon=True,
        )
        self._thread.start()

    def disconnect(self, *, timeout: float = 2.0) -> None:
        """Close the WebSocket connection and wait briefly for shutdown."""
        if self._ws is not None:
            try:
                self._ws.close()
            except (RuntimeError, OSError):  # best-effort close
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    # -------------------------- internal logic ------------------------
    def _build_ws_url(self) -> str:
        clean_token = Helpers.clean_token(self.access_token)
        ts = Helpers.timestamp()

        # Determine region from token using existing helper
        endpoint = Helpers.parse_token_and_get_endpoint(self.access_token)
        region_code = "eu" if endpoint == EU_BASE_URL else "us"

        base = WS_BASE_URL.format(region_code)
        path = ENDPOINTS["WS_LOGIN"].format(clean_token, ts)
        return base + path

    # -------------------------- ws callbacks --------------------------
    def _on_open(self, _ws) -> None:
        self._connected = True
        self._logger.debug("WebSocket opened")
        if self._user_on_open:
            try:
                self._user_on_open()
            except (RuntimeError, OSError) as exc:  # user callback errors should not kill ws
                self._logger.warning("on_open callback error: %s", exc)

    def _on_message(self, _ws, message: str) -> None:
        if self._user_on_message:
            try:
                self._user_on_message(message)
            except (RuntimeError, OSError) as exc:
                self._logger.warning("on_message callback error: %s", exc)

    def _on_error(self, _ws, error: Exception) -> None:
        self._logger.debug("WebSocket error: %s", error)
        if self._user_on_error:
            try:
                self._user_on_error(error)
            except (RuntimeError, OSError) as exc:
                self._logger.warning("on_error callback error: %s", exc)

    def _on_close(self, _ws, status_code: Optional[int], reason: Optional[str]) -> None:
        self._connected = False
        self._logger.debug("WebSocket closed: code=%s reason=%s", status_code, reason)
        if self._user_on_close:
            try:
                self._user_on_close(status_code, reason)
            except (RuntimeError, OSError) as exc:
                self._logger.warning("on_close callback error: %s", exc)


