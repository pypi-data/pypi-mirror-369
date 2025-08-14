# Gotty Python Client

A generic Python client for interacting with gotty terminal interfaces.

## What is Gotty?

[Gotty](https://github.com/sorear/gotty) is a tool that turns terminal applications into web applications. It provides a WebSocket interface that allows you to interact with terminal applications through a web browser.

## Features

- **Generic gotty protocol support**: Works with any gotty terminal interface
- **WebSocket communication**: Real-time bidirectional communication
- **Authentication support**: Basic HTTP authentication
- **Command execution**: Send commands and receive responses
- **Terminal output buffering**: Maintains history of terminal output
- **Threading support**: Background message handling
- **Callback system**: Real-time output and command callbacks

## Security Considerations

⚠️ **IMPORTANT SECURITY WARNINGS**

This client has several security considerations you should be aware of:

1. **Insecure by Default**: The client uses unencrypted WebSocket connections (`ws://`) by default. For production use, ensure your gotty server supports secure WebSocket connections (`wss://`).

2. **Plain Text Credentials**: Credentials are stored and transmitted in plain text. Consider using environment variables or secure credential management.

3. **Command Injection**: The client sends commands directly to the terminal. Validate and sanitize all commands before sending them.

4. **Network Exposure**: This client can execute commands on remote systems. Use with caution and only connect to trusted servers.

5. **No Input Validation**: The client performs minimal input validation. Always validate URLs, usernames, and commands before use.

**Best Practices:**
- Use HTTPS/WSS connections in production
- Store credentials in environment variables
- Validate all inputs before use
- Only connect to trusted gotty servers
- Monitor and log all command executions

## Installation

```bash
pip install gotty-py
```

## Quick Start

```python
from gotty_py import GottyWebSocketClient
import os

# Create a client with environment variables for security
client = GottyWebSocketClient(
    webui_url=os.getenv("GOTTY_URL", "http://localhost:8222"),
    username=os.getenv("GOTTY_USERNAME", "admin"),
    password=os.getenv("GOTTY_PASSWORD", "password")
)

# Connect to the gotty interface
if client.connect():
    print("Connected successfully!")
    
    # Execute a command
    response = client.execute_command("ls -la")
    if response.success:
        print("Command output:", response.data)
    
    # Close the connection
    client.close()
```

## Usage

### Basic Connection

```python
from gotty_py import GottyWebSocketClient
import os

client = GottyWebSocketClient(
    webui_url=os.getenv("GOTTY_URL", "http://your-server:port"),
    username=os.getenv("GOTTY_USERNAME", "your_username"),
    password=os.getenv("GOTTY_PASSWORD", "your_password")
)

# Connect
if client.connect():
    print("Connected!")
else:
    print("Connection failed!")
```

### Executing Commands

```python
# Execute a command and wait for response
response = client.execute_command("echo 'Hello, World!'")
if response.success:
    print("Output:", response.data)
else:
    print("Error:", response.message)

# Execute a command without waiting for response
response = client.execute_command("long_running_command", wait_for_response=False)
```

### Getting Terminal Output

```python
# Get all terminal output
output = client.get_terminal_output()

# Get last 10 lines
recent_output = client.get_terminal_output(last_n_lines=10)

# Get command history
history = client.get_command_history()
```

### Real-time Callbacks

```python
def on_output(data):
    print(f"New output: {data}")

def on_command(cmd):
    print(f"Command executed: {cmd}")

# Add callbacks
client.add_output_callback(on_output)
client.add_command_callback(on_command)
```

## API Reference

### GottyWebSocketClient

#### Constructor

```python
GottyWebSocketClient(
    webui_url: str,
    username: str,
    password: str,
    timeout: int = 30
)
```

#### Methods

- `connect() -> bool`: Connect to the gotty WebSocket interface
- `execute_command(command: str, wait_for_response: bool = True, timeout: float = 10.0) -> ServerResponse`: Execute a command
- `send_command(command: str) -> bool`: Send a command without waiting for response
- `get_terminal_output(last_n_lines: Optional[int] = None) -> List[str]`: Get terminal output
- `get_command_history() -> List[str]`: Get command history
- `add_output_callback(callback: Callable[[str], None])`: Add output callback
- `add_command_callback(callback: Callable[[str], None])`: Add command callback
- `close()`: Close the connection

### ServerResponse

```python
@dataclass
class ServerResponse:
    success: bool
    data: Any
    message: str
    status_code: int
```

## Examples

### Minecraft Server Integration

```python
from gotty_py import GottyWebSocketClient

# Connect to a Minecraft server with gotty
client = GottyWebSocketClient(
    webui_url="http://minecraft-server:8222",
    username="admin",
    password="minecraft"
)

if client.connect():
    # List players
    response = client.execute_command("list")
    if response.success:
        print("Players:", response.data)
    
    # Give items
    client.execute_command("give player diamond_sword 1")
    
    client.close()
```

### SSH Terminal

```python
from gotty_py import GottyWebSocketClient

# Connect to an SSH terminal via gotty
client = GottyWebSocketClient(
    webui_url="http://ssh-server:8080",
    username="user",
    password="pass"
)

if client.connect():
    # Run commands
    client.execute_command("pwd")
    client.execute_command("ls -la")
    client.execute_command("whoami")
    
    client.close()
```

## Development

### Installation for Development

```bash
git clone https://github.com/twentworth/gotty-py.git
cd gotty-py
pip install -e .
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run unit tests only (safe for CI)
pytest -m "not integration"

# Run integration tests (requires real gotty server)
pytest -m "integration"

# Run all tests
pytest
```

**Note:** Integration tests require a real gotty server to be running. These tests are excluded from CI/CD pipelines since they need external infrastructure.

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy .
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
