"""Configuration parsing utilities for different MCP server formats."""

import json
import re
import sys
from typing import Any
from urllib.parse import urlparse

from mcpcommander.schemas.config_schema import ServerConfig
from mcpcommander.utils.errors import ValidationError
from mcpcommander.utils.logger import get_logger

logger = get_logger(__name__)


def get_safe_line_char() -> str:
    """Get appropriate line character based on encoding support."""
    try:
        "═".encode(sys.stdout.encoding or "utf-8")
        return "═"
    except (UnicodeEncodeError, LookupError, AttributeError):
        return "-"


class ServerConfigParser:
    """Parser for various MCP server configuration formats."""

    @staticmethod
    def parse_server_config(
        config_input: str | dict[str, Any], env_vars: dict[str, str] | None = None
    ) -> ServerConfig:
        """Parse server configuration from various input formats.

        Supported formats:
        1. Command string: "npx server-package"
        2. JSON string: '{"command": "npx", "args": ["server-package"]}'
        3. JSON with transport: '{"transport": {"type": "http", "host": "localhost", "port": 3000}}'
        4. Dict object with any of the above structures

        Args:
            config_input: Configuration input in various formats
            env_vars: Optional environment variables to add to the configuration

        Returns:
            Validated ServerConfig object

        Raises:
            ValidationError: If configuration is invalid
        """
        try:
            # If it's already a dict, use it directly
            if isinstance(config_input, dict):
                config_dict = config_input.copy()
            elif isinstance(config_input, str):
                config_dict = ServerConfigParser._parse_string_input(config_input)
            else:
                raise ValidationError(f"Unsupported configuration type: {type(config_input)}")

            # Add environment variables if provided
            if env_vars:
                # Merge with existing env vars if any
                existing_env = config_dict.get("env", {})
                if existing_env:
                    # CLI options override existing env vars
                    merged_env = existing_env.copy()
                    merged_env.update(env_vars)
                    config_dict["env"] = merged_env
                else:
                    config_dict["env"] = env_vars

            # Create and validate ServerConfig
            return ServerConfig(**config_dict)

        except Exception as e:
            logger.error(f"Failed to parse server configuration: {e}")
            raise ValidationError(f"Invalid server configuration: {e}") from e

    @staticmethod
    def _parse_string_input(config_str: str) -> dict[str, Any]:
        """Parse string input into configuration dict."""
        config_str = config_str.strip()

        # Try parsing as JSON first
        if config_str.startswith("{"):
            try:
                parsed_data: dict[str, Any] = json.loads(config_str)
                return parsed_data
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON configuration: {e}") from e

        # Check if it's a URL (for quick transport creation)
        if ServerConfigParser._is_url(config_str):
            return ServerConfigParser._url_to_transport_config(config_str)

        # Treat as command string
        return ServerConfigParser._command_to_config(config_str)

    @staticmethod
    def _is_url(text: str) -> bool:
        """Check if text looks like a URL."""
        return text.startswith(("http://", "https://", "ws://", "wss://"))

    @staticmethod
    def _url_to_transport_config(url: str) -> dict[str, Any]:
        """Convert URL to transport configuration."""
        parsed = urlparse(url)

        if parsed.scheme in ("ws", "wss"):
            return {"transport": {"type": "websocket", "url": url}}
        elif parsed.scheme in ("http", "https"):
            # Check for common SSE patterns in URL
            sse_indicators = ["stream", "sse", "events", "event", "feed"]
            if any(indicator in url.lower() for indicator in sse_indicators):
                return {"transport": {"type": "sse", "url": url}}
            else:
                # Default to HTTP transport for other HTTPS URLs
                return {
                    "transport": {
                        "type": "http",
                        "host": parsed.hostname or "localhost",
                        "port": parsed.port or (443 if parsed.scheme == "https" else 80),
                        "path": parsed.path or "/mcp",
                    }
                }
        else:
            raise ValidationError(f"Unsupported URL scheme: {parsed.scheme}")

    @staticmethod
    def _command_to_config(command_str: str) -> dict[str, Any]:
        """Convert command string to STDIO configuration."""
        # Simple shell-like parsing
        parts = ServerConfigParser._split_command(command_str)
        if not parts:
            raise ValidationError("Empty command")

        return {"command": parts[0], "args": parts[1:] if len(parts) > 1 else None}

    @staticmethod
    def _split_command(command_str: str) -> list[str]:
        """Split command string into parts, handling quotes and paths with spaces."""
        import shlex

        # First try direct shlex parsing
        basic_result = shlex.split(command_str)

        # Check if the result looks problematic (first token looks like a broken path)
        if (
            len(basic_result) > 1
            and basic_result[0].startswith("/")
            and not basic_result[0].endswith(("/", ".exe", ".bat"))
            and ServerConfigParser._looks_like_broken_path(basic_result)
        ):
            # Try smart parsing instead
            return ServerConfigParser._smart_split_with_auto_quoting(command_str)

        return basic_result

    @staticmethod
    def _looks_like_broken_path(parts: list[str]) -> bool:
        """Check if the split result looks like a broken path with spaces."""
        if len(parts) < 2:
            return False

        first_part = parts[0]

        # Signs this might be a broken path:
        # 1. First part ends abruptly (not with a complete directory/file name)
        # 2. Looking for common macOS app patterns
        # 3. Common keywords that suggest a path was split incorrectly
        return first_part.startswith("/Applications/") or (
            first_part.count("/") > 2
            and any(
                keyword in " ".join(parts[:3]).lower()
                for keyword in ["suite", "edition", "community", "program files"]
            )
        )

    @staticmethod
    def _smart_split_with_auto_quoting(command_str: str) -> list[str]:
        """Intelligently split command by auto-quoting paths with spaces."""
        import shlex

        # Common patterns for executable paths that might contain spaces
        executable_patterns = [
            # macOS .app bundles with spaces in name: /Applications/Name With Spaces.app/Contents/...
            r"^(/Applications/[^/]+(?:\s+[^/]+)*\.app/[^\s]+)",
            # General Unix paths with spaces leading to common executables
            r"^(/[^\s]+(?:\s+[^\s]+)+(?:/[^\s]*)*(?:java|python|node|bin)(?:\s|$))",
            # Catch any path that starts with / and contains spaces, ending in common executable names
            r"^(/[^/]*(?:\s+[^/]*)+[^/]*/(?:java|python|node|bin))",
            # Windows Program Files
            r"^(C:\\Program Files[^\\]*(?:\\[^\\]+)*)",
        ]

        # Try to detect and quote executable paths automatically
        for pattern in executable_patterns:
            match = re.match(pattern, command_str, re.IGNORECASE)
            if match:
                executable_path = match.group(1)
                remainder = command_str[match.end() :].lstrip()

                # Use single quotes to avoid conflicts with double quotes in the outer command
                quoted_command = (
                    f"'{executable_path}' {remainder}" if remainder else f"'{executable_path}'"
                )

                logger.info(f"Auto-quoting detected executable path with spaces: {executable_path}")

                try:
                    return shlex.split(quoted_command)
                except ValueError:
                    continue  # Try next pattern

        # If no patterns match, fall back to basic regex splitting
        logger.warning("Using fallback regex parsing - consider quoting paths with spaces manually")
        pattern = r'[^\s"\']+|"[^"]*"|\'[^\']*\''
        parts = re.findall(pattern, command_str)
        return [part.strip("'\"") for part in parts]


def create_example_configs() -> dict[str, dict[str, Any]]:
    """Create example configurations for different transport types."""
    return {
        "stdio-simple": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/user"],
        },
        "stdio-with-env": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {"BRAVE_API_KEY": "your-api-key"},
        },
        "http-transport": {
            "transport": {"type": "http", "host": "localhost", "port": 3000, "path": "/mcp"}
        },
        "websocket-transport": {
            "transport": {
                "type": "websocket",
                "url": "ws://localhost:8080/mcp",
                "headers": {"X-API-Key": "your-key"},
            }
        },
        "sse-transport": {
            "transport": {"type": "sse", "url": "https://notifications.example.com/mcp/stream"}
        },
    }


def print_transport_examples() -> None:
    """Print examples of different transport configurations."""
    from rich.console import Console
    from rich.syntax import Syntax

    console = Console(legacy_windows=True, force_terminal=True)
    examples = create_example_configs()

    line_char = get_safe_line_char()
    console.print("\n[bold cyan]MCP Server Configuration Examples[/bold cyan]")
    console.print(f"[dim]{line_char * 50}[/dim]")

    for name, config in examples.items():
        console.print(f"\n[bold green]• {name.replace('-', ' ').title()}:[/bold green]")
        json_str = json.dumps(config, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)
