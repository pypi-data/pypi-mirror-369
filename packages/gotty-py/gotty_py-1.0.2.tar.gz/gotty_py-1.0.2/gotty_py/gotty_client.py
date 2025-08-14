"""
Generic Gotty WebSocket Client

This module provides a WebSocket client for interacting with any gotty terminal interface.
"""

import asyncio
import json
import time
import logging
import threading
import base64
import os
from typing import Optional, List, Callable, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
import websockets
from websockets.exceptions import WebSocketException

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ServerResponse:
    """Container for server response data."""
    success: bool
    data: Any
    message: str
    status_code: int

class GottyWebSocketClient:
    """
    Generic WebSocket client for communicating with gotty terminal interfaces.
    
    This client follows the gotty protocol:
    - Uses "webtty" subprotocol
    - Sends initial handshake with auth token
    - Messages are prefixed with type identifiers
    - Input messages use '1' prefix
    - Output messages are base64 encoded
    """
    
    def __init__(
        self, 
        webui_url: str,
        username: str,
        password: str,
        timeout: int = 30
    ):
        """
        Initialize the gotty WebSocket client.
        
        Args:
            webui_url: URL of the web UI (e.g., 'http://localhost:8222')
            username: Web UI username
            password: Web UI password
            timeout: Connection timeout in seconds
        """
        # Input validation
        if not webui_url or not isinstance(webui_url, str):
            raise ValueError("webui_url must be a non-empty string")
        
        if not username or not isinstance(username, str):
            raise ValueError("username must be a non-empty string")
            
        if not password or not isinstance(password, str):
            raise ValueError("password must be a non-empty string")
            
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("timeout must be a positive integer")
        
        # Validate URL format
        parsed_url = urlparse(webui_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format. Expected format: http://host:port")
        
        # Warn about insecure connections
        if parsed_url.scheme == 'http':
            logger.warning("Using insecure HTTP connection. Consider using HTTPS for production.")
        
        self.webui_url = webui_url
        self.username = username
        self.password = password
        self.timeout = timeout
        
        # WebSocket connection
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.connected = False
        
        # Terminal state
        self.terminal_output: List[str] = []
        self.current_line = ""
        self.command_history: List[str] = []
        
        # Threading for background operations
        self._listener_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Callbacks for real-time updates
        self._output_callbacks: List[Callable[[str], None]] = []
        self._command_callbacks: List[Callable[[str], None]] = []
        
        # Parse the webui URL
        self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Construct WebSocket URL with gotty protocol
        auth_token = f"{self.username}:{self.password}"
        
        # Use WSS for HTTPS, WS for HTTP
        if parsed_url.scheme == 'https':
            self.ws_url = f"wss://{parsed_url.netloc}/ws"
            logger.info("Using secure WebSocket connection (WSS)")
        else:
            self.ws_url = f"ws://{parsed_url.netloc}/ws"
            logger.warning("Using insecure WebSocket connection (WS). Consider using HTTPS for production.")
            
        self.auth_token = auth_token
        
    def connect(self) -> bool:
        """Connect to the gotty WebSocket interface."""
        try:
            # Test HTTP connection first with authentication
            response = requests.get(
                self.webui_url, 
                auth=(self.username, self.password),
                timeout=5
            )
            if response.status_code != 200:
                logger.error(f"Web UI not accessible: {response.status_code}")
                return False
            
            # Start the background listener thread
            self._start_listener()
            
            # Wait for connection to be established
            start_time = time.time()
            while not self.connected and time.time() - start_time < 10:
                time.sleep(0.1)
            
            if self.connected:
                logger.info(f"CONNECTION_SUCCESS - User: {self.username}, Server: {self.webui_url}")
            else:
                logger.error(f"CONNECTION_TIMEOUT - User: {self.username}, Server: {self.webui_url}")
            
            return self.connected
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def _start_listener(self):
        """Start the background WebSocket listener thread."""
        if self._listener_thread and self._listener_thread.is_alive():
            return
        
        self._running = True
        self._listener_thread = threading.Thread(target=self._run_listener, daemon=True)
        self._listener_thread.start()
    
    def _run_listener(self):
        """Run the WebSocket listener in a background thread."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._event_loop = loop
            
            # Run the async listener
            loop.run_until_complete(self._listen_websocket())
            
        except Exception as e:
            logger.error(f"Listener thread error: {e}")
        finally:
            self._running = False
    
    async def _listen_websocket(self):
        """Listen for WebSocket messages."""
        try:
            logger.info(f"Connecting to WebSocket: {self.ws_url}")
            
            # Connect with gotty protocol
            self.websocket = await websockets.connect(
                self.ws_url,
                subprotocols=["webtty"],
                additional_headers={
                    'Authorization': f'Basic {self._get_auth_header()}',
                    'User-Agent': 'GottyPythonClient/1.0'
                },
                ping_interval=30,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.connected = True
            logger.info("WebSocket connected successfully")
            
            # Send initial handshake
            await self._send_handshake()
            
            # Listen for messages
            logger.debug("Starting to listen for WebSocket messages...")
            async for message in self.websocket:
                logger.debug(f"Raw message received: {repr(message)}")
                await self._handle_message(message)
                
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.connected = False
            if self.websocket:
                await self.websocket.close()
            logger.info("WebSocket connection closed")
    
    async def _send_handshake(self):
        """Send the initial handshake message."""
        handshake = {
            "Arguments": "",
            "AuthToken": self.auth_token
        }
        handshake_data = json.dumps(handshake)
        logger.debug(f"Sending handshake: {handshake_data}")
        await self.websocket.send(handshake_data)
    
    async def _handle_message(self, message):
        """Handle incoming WebSocket messages."""
        try:
            if not message:
                return
            
            # Parse message type
            msg_type = message[0]
            payload = message[1:] if len(message) > 1 else ""
            
            logger.debug(f"Message type: {msg_type}, payload: {repr(payload)}")
            
            if msg_type == '1':  # Output message
                # Decode base64 payload
                try:
                    decoded_data = base64.b64decode(payload).decode('utf-8', errors='ignore')
                    logger.debug(f"Decoded output: {repr(decoded_data)}")
                    
                    # Process the terminal output
                    with self._lock:
                        self.terminal_output.append(decoded_data)
                        
                        # Keep only last 1000 lines to prevent memory issues
                        if len(self.terminal_output) > 1000:
                            self.terminal_output = self.terminal_output[-1000:]
                        
                        # Update current line
                        if decoded_data.endswith('\n'):
                            # Complete line
                            self.current_line += decoded_data.rstrip('\n')
                            if self.current_line.strip():
                                self.command_history.append(self.current_line.strip())
                                # Keep only last 100 commands
                                if len(self.command_history) > 100:
                                    self.command_history = self.command_history[-100:]
                            self.current_line = ""
                        else:
                            # Partial line
                            self.current_line += decoded_data
                    
                    # Notify callbacks
                    for callback in self._output_callbacks:
                        try:
                            callback(decoded_data)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                            
                except Exception as e:
                    logger.error(f"Failed to decode output message: {e}")
                    
            elif msg_type == '2':  # Pong message
                logger.debug("Received pong")
                
            elif msg_type == '3':  # Set window title
                logger.debug(f"Window title: {payload}")
                
            elif msg_type == '4':  # Set preferences
                logger.debug(f"Preferences: {payload}")
                
            elif msg_type == '5':  # Set reconnect
                logger.debug(f"Reconnect: {payload}")
                
            else:
                logger.debug(f"Unknown message type: {msg_type}")
                    
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def _get_auth_header(self) -> str:
        """Get base64 encoded authentication header."""
        import base64
        auth_string = f"{self.username}:{self.password}"
        return base64.b64encode(auth_string.encode()).decode()
    
    def send_command(self, command: str) -> bool:
        """
        Send a command using the gotty protocol.
        
        Args:
            command: Command to send
            
        Returns:
            True if sent successfully
        """
        # Input validation
        if not command or not isinstance(command, str):
            logger.error("Command must be a non-empty string")
            return False
        
        # Basic command injection prevention
        dangerous_patterns = [
            ';', '&&', '||', '|', '>', '<', '`', '$(',
            'eval', 'exec', 'system', 'subprocess'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logger.warning(f"Potentially dangerous command pattern detected: {pattern}")
                # You might want to raise an exception here instead of just warning
                # raise ValueError(f"Dangerous command pattern detected: {pattern}")
        
        if not self.connected or not self.websocket:
            logger.error("Not connected to WebSocket")
            return False
        
        try:
            # Format command according to gotty protocol
            # Input messages are prefixed with '1'
            # Add newline to execute the command
            command_data = '1' + command + '\n'
            logger.debug(f"Sending command '{command}' as: {repr(command_data)}")
            
            if self._event_loop:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send(command_data),
                    self._event_loop
                )
                logger.debug(f"Command '{command}' sent successfully")
                return True
            else:
                logger.error("Event loop not initialized for sending command.")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send command: {e}")
            return False
    
    def execute_command(self, command: str, wait_for_response: bool = True, timeout: float = 10.0) -> ServerResponse:
        """
        Execute a command and optionally wait for response.
        
        Args:
            command: Command to execute
            wait_for_response: Whether to wait for command completion
            timeout: Timeout for response in seconds
            
        Returns:
            ServerResponse with command result
        """
        if not self.connected:
            return ServerResponse(
                success=False,
                data=None,
                message="Not connected to WebSocket",
                status_code=0
            )
        
        try:
            # Get current output length
            initial_output_length = len(self.terminal_output)
            
            # Send the command
            if not self.send_command(command):
                return ServerResponse(
                    success=False,
                    data=None,
                    message="Failed to send command",
                    status_code=0
                )
            
            if not wait_for_response:
                return ServerResponse(
                    success=True,
                    data=None,
                    message="Command sent (no response requested)",
                    status_code=200
                )
            
            # Wait for response
            start_time = time.time()
            while time.time() - start_time < timeout:
                with self._lock:
                    if len(self.terminal_output) > initial_output_length:
                        # Get new output
                        new_output = self.terminal_output[initial_output_length:]
                        return ServerResponse(
                            success=True,
                            data=new_output,
                            message="Command executed successfully",
                            status_code=200
                        )
                time.sleep(0.1)
            
            # Timeout
            return ServerResponse(
                success=False,
                data=None,
                message="Command timed out",
                status_code=408
            )
            
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return ServerResponse(
                success=False,
                data=None,
                message=f"Command failed: {e}",
                status_code=0
            )
    
    def get_terminal_output(self, last_n_lines: Optional[int] = None) -> List[str]:
        """
        Get terminal output.
        
        Args:
            last_n_lines: Number of lines to return (None for all)
            
        Returns:
            List of terminal output lines
        """
        with self._lock:
            if last_n_lines is None:
                return self.terminal_output.copy()
            else:
                return self.terminal_output[-last_n_lines:].copy()
    
    def get_command_history(self) -> List[str]:
        """Get command history."""
        with self._lock:
            return self.command_history.copy()
    
    def add_output_callback(self, callback: Callable[[str], None]):
        """Add a callback for real-time output updates."""
        self._output_callbacks.append(callback)
    
    def add_command_callback(self, callback: Callable[[str], None]):
        """Add a callback for command completions."""
        self._command_callbacks.append(callback)
    
    def close(self):
        """Close the WebSocket connection."""
        self._running = False
        self.connected = False
        
        if self._listener_thread and self._listener_thread.is_alive():
            self._listener_thread.join(timeout=5)
        
        if self.websocket:
            try:
                asyncio.run_coroutine_threadsafe(
                    self.websocket.close(),
                    self._event_loop
                )
            except:
                pass
