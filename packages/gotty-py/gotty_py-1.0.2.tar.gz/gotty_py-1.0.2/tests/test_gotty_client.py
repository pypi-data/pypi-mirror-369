"""
Tests for the GottyWebSocketClient class.
"""

import threading
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from gotty_py import GottyWebSocketClient, ServerResponse


class TestGottyWebSocketClient:
    """Test cases for GottyWebSocketClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = GottyWebSocketClient(
            webui_url="http://192.168.0.113:8222",
            username="admin",
            password="admin",
            timeout=30,
        )

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, "client"):
            self.client.close()

    def test_initialization(self):
        """Test client initialization."""
        assert self.client.webui_url == "http://192.168.0.113:8222"
        assert self.client.username == "admin"
        assert self.client.password == "admin"
        assert self.client.timeout == 30
        assert not self.client.connected
        assert self.client.websocket is None
        assert self.client.terminal_output == []
        assert self.client.command_history == []

    def test_auth_header_generation(self):
        """Test authentication header generation."""
        auth_header = self.client._get_auth_header()
        expected = "YWRtaW46YWRtaW4="  # base64 of "admin:admin"
        assert auth_header == expected

    def test_url_parsing(self):
        """Test URL parsing for WebSocket connection."""
        assert self.client.base_url == "http://192.168.0.113:8222"
        assert self.client.ws_url == "ws://192.168.0.113:8222/ws"
        assert self.client.auth_token == "admin:admin"

    @patch("requests.get")
    def test_connect_http_failure(self, mock_get):
        """Test connection failure when HTTP request fails."""
        mock_get.return_value.status_code = 401

        result = self.client.connect()
        assert not result
        assert not self.client.connected

    @patch("requests.get")
    def test_connect_http_exception(self, mock_get):
        """Test connection failure when HTTP request raises exception."""
        mock_get.side_effect = Exception("Connection error")

        result = self.client.connect()
        assert not result
        assert not self.client.connected

    @patch("requests.get")
    @patch("websockets.connect")
    def test_connect_success(self, mock_ws_connect, mock_get):
        """Test successful connection."""
        # Mock HTTP response
        mock_get.return_value.status_code = 200

        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_ws_connect.return_value = mock_websocket

        # Mock the async listener
        with patch.object(self.client, "_listen_websocket") as mock_listen:
            mock_listen.return_value = None

            # Start connection in a thread to avoid blocking
            def connect():
                self.client.connect()

            thread = threading.Thread(target=connect)
            thread.start()

            # Wait a bit for connection to establish
            time.sleep(0.1)

            # Stop the client
            self.client.close()
            thread.join(timeout=1)

    def test_send_command_not_connected(self):
        """Test sending command when not connected."""
        result = self.client.send_command("ls")
        assert not result

    @patch("asyncio.run_coroutine_threadsafe")
    def test_send_command_success(self, mock_run_coroutine):
        """Test successful command sending."""
        # Mock connection state
        self.client.connected = True
        self.client.websocket = AsyncMock()
        self.client._event_loop = Mock()

        result = self.client.send_command("ls")
        assert result
        mock_run_coroutine.assert_called_once()

    def test_execute_command_not_connected(self):
        """Test executing command when not connected."""
        response = self.client.execute_command("ls")
        assert not response.success
        assert response.message == "Not connected to WebSocket"
        assert response.status_code == 0

    def test_execute_command_send_failure(self):
        """Test command execution when send fails."""
        # Mock connection state
        self.client.connected = True

        with patch.object(self.client, "send_command", return_value=False):
            response = self.client.execute_command("ls")
            assert not response.success
            assert response.message == "Failed to send command"

    def test_execute_command_no_wait(self):
        """Test command execution without waiting for response."""
        # Mock connection state
        self.client.connected = True

        with patch.object(self.client, "send_command", return_value=True):
            response = self.client.execute_command("ls", wait_for_response=False)
            assert response.success
            assert response.message == ("Command sent (no response requested)")
            assert response.status_code == 200

    def test_get_terminal_output(self):
        """Test getting terminal output."""
        # Add some test data
        self.client.terminal_output = ["line1", "line2", "line3"]

        # Get all output
        output = self.client.get_terminal_output()
        assert output == ["line1", "line2", "line3"]

        # Get last 2 lines
        output = self.client.get_terminal_output(last_n_lines=2)
        assert output == ["line2", "line3"]

    def test_get_command_history(self):
        """Test getting command history."""
        # Add some test data
        self.client.command_history = ["ls", "pwd", "whoami"]

        history = self.client.get_command_history()
        assert history == ["ls", "pwd", "whoami"]

    def test_add_callbacks(self):
        """Test adding callbacks."""

        def test_callback(data):
            pass

        self.client.add_output_callback(test_callback)
        self.client.add_command_callback(test_callback)

        assert len(self.client._output_callbacks) == 1
        assert len(self.client._command_callbacks) == 1

    def test_close(self):
        """Test closing the connection."""
        # Mock thread
        self.client._listener_thread = Mock()
        self.client._listener_thread.is_alive.return_value = False

        # Mock WebSocket
        self.client.websocket = AsyncMock()
        self.client._event_loop = Mock()

        self.client.close()

        assert not self.client._running
        assert not self.client.connected


class TestServerResponse:
    """Test cases for ServerResponse dataclass."""

    def test_server_response_creation(self):
        """Test ServerResponse creation."""
        response = ServerResponse(
            success=True, data=["output"], message="Success", status_code=200
        )

        assert response.success is True
        assert response.data == ["output"]
        assert response.message == "Success"
        assert response.status_code == 200


# Integration tests (these require a real server)
class TestGottyClientIntegration:
    """Integration tests that require a real gotty server."""

    @pytest.mark.integration
    def test_real_connection(self):
        """Test connection to real gotty server."""
        client = GottyWebSocketClient(
            webui_url="http://192.168.0.113:8222",
            username="admin",
            password="admin",
        )

        try:
            # This test requires the server to be running
            # We'll just test the connection attempt
            client.connect()
            # Note: This might fail if server is not available
            # That's expected in CI environments
        finally:
            client.close()

    @pytest.mark.integration
    def test_real_command_execution(self):
        """Test command execution on real server."""
        client = GottyWebSocketClient(
            webui_url="http://192.168.0.113:8222",
            username="admin",
            password="admin",
        )

        try:
            if client.connect():
                # Test the "ls" command
                response = client.execute_command("ls", timeout=5.0)
                # We expect some response, even if it's an error
                assert response is not None
        finally:
            client.close()


if __name__ == "__main__":
    # Run integration tests if server is available
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--integration":
        # Run integration tests
        pytest.main([__file__, "-m", "integration", "-v"])
    else:
        # Run unit tests only
        pytest.main([__file__, "-m", "not integration", "-v"])
