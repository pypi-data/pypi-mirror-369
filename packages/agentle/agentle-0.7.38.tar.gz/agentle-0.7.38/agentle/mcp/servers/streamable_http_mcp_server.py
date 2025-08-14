"""
Production-ready fixes for StreamableHTTPMCPServer using aiohttp

This version is a refactor of the original httpx-based implementation.

Key changes:
1. Replaced httpx.AsyncClient with aiohttp.ClientSession for connection pooling.
2. Adapted exception handling to aiohttp-specific errors (e.g., aiohttp.ClientError).
3. Updated response handling to use await on methods like .json() and .text().
4. Maintained all original functionality, retry logic, and session management.
5. FIXED: JSON-RPC 2.0 compliance - only include params when they exist and are not empty.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import AsyncIterator, Callable, MutableMapping, Sequence
from typing import TYPE_CHECKING, Any, Dict, Optional

import aiohttp
from aiohttp import ClientTimeout, TCPConnector
from rsb.models.field import Field
from rsb.models.private_attr import PrivateAttr

from agentle.mcp.servers.mcp_server_protocol import MCPServerProtocol
from agentle.mcp.session_management import SessionManager, InMemorySessionManager

if TYPE_CHECKING:
    from mcp.types import (
        BlobResourceContents,
        CallToolResult,
        Resource,
        TextResourceContents,
        Tool,
    )


class StreamableHTTPMCPServer(MCPServerProtocol):
    """
    Production-ready Streamable HTTP implementation of MCP server client using aiohttp.

    This version uses aiohttp.ClientSession for improved performance and follows
    the library's best practices.
    """

    # Configuration fields
    server_name: str = Field(..., description="Human-readable name for the MCP server")
    server_url: str = Field(..., description="Base URL for the HTTP MCP server")
    mcp_endpoint: str | Callable[..., str] = Field(
        default="/mcp", description="The endpoint path for MCP requests"
    )
    headers: MutableMapping[str, str] = Field(
        default_factory=dict, description="Custom HTTP headers"
    )
    timeout_s: float = Field(default=100.0, description="Request timeout in seconds")
    session_manager: SessionManager = Field(
        default_factory=InMemorySessionManager, description="Session manager"
    )

    # Production settings
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay_s: float = Field(default=1.0, description="Base retry delay")
    connection_pool_limits: Dict[str, int] = Field(
        default_factory=lambda: {
            "max_keepalive_connections": 20,
            "max_connections": 100,
        },
        description="Connection pool limits",
    )

    # Internal state
    _logger: logging.Logger = PrivateAttr(
        default_factory=lambda: logging.getLogger(__name__)
    )
    _client: Optional[aiohttp.ClientSession] = PrivateAttr(default=None)
    _session_id: Optional[str] = PrivateAttr(default=None)
    _last_event_id: Optional[str] = PrivateAttr(default=None)
    _jsonrpc_id_counter: int = PrivateAttr(default=1)
    _initialized: bool = PrivateAttr(default=False)
    _connection_lock: asyncio.Lock = PrivateAttr(default_factory=asyncio.Lock)

    @property
    def name(self) -> str:
        return self.server_name

    @property
    def _server_key(self) -> str:
        return f"{self.server_url}:{self.mcp_endpoint}"

    def _is_connected(self) -> bool:
        """Check if client is connected and valid."""
        return (
            self._client is not None and not self._client.closed and self._initialized
        )

    def _create_client(self) -> aiohttp.ClientSession:
        """Create a new aiohttp client session with connection pooling."""
        base_headers = {
            "Accept": "application/json, text/event-stream",
            "Cache-Control": "no-cache",
            "User-Agent": "agentle-mcp-client/0.1.0-aiohttp",
        }

        all_headers = {**base_headers, **self.headers}

        # Use aiohttp's TCPConnector for connection pooling
        connector = TCPConnector(
            limit=self.connection_pool_limits.get("max_connections", 100),
            limit_per_host=self.connection_pool_limits.get(
                "max_keepalive_connections", 20
            ),
        )

        timeout = ClientTimeout(total=self.timeout_s)

        return aiohttp.ClientSession(
            base_url=str(self.server_url),
            headers=all_headers,
            timeout=timeout,
            connector=connector,
        )

    async def connect_async(self) -> None:
        """Connect with proper session restoration and validation."""
        async with self._connection_lock:
            if self._is_connected():
                return

            self._logger.info(f"Connecting to HTTP server: {self.server_url}")

            server_key = self._server_key
            session_data = await self.session_manager.get_session(server_key)

            if session_data is not None:
                self._logger.debug(f"Found existing session for {server_key}")
                self._session_id = session_data.get("session_id")
                self._last_event_id = session_data.get("last_event_id")
                self._jsonrpc_id_counter = session_data.get("jsonrpc_counter", 1)

            await self._establish_connection()

    async def _establish_connection(self) -> None:
        """Establish HTTP client and initialize protocol."""
        try:
            if self._client and not self._client.closed:
                await self._client.close()

            self._client = self._create_client()

            await self._health_check()

            if not self._initialized:
                await self._initialize_protocol()

            await self._store_session_data()
            self._initialized = True
            self._logger.info("HTTP MCP connection established successfully")

        except Exception as e:
            self._logger.error(f"Error establishing connection: {e}")
            self._initialized = False
            await self._cleanup_client()
            raise ConnectionError(f"Could not connect to server {self.server_url}: {e}")

    async def _health_check(self) -> None:
        """Perform a health check to validate connection."""
        if not self._client:
            raise ConnectionError("Client not initialized")

        try:
            timeout = ClientTimeout(total=5.0)
            async with self._client.get(
                "/health", timeout=timeout, allow_redirects=True
            ) as response:
                if response.status >= 500:
                    raise ConnectionError(f"Server error: {response.status}")
        except aiohttp.ClientConnectorError as e:
            raise ConnectionError(f"Cannot connect to server: {e}")
        except asyncio.TimeoutError as e:
            raise ConnectionError(f"Connection timeout: {e}")

    async def _initialize_protocol(self) -> None:
        """Initialize MCP protocol with retry logic."""
        self._logger.info("Initializing MCP protocol")

        initialize_request: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": str(self._jsonrpc_id_counter),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "agentle-mcp-client", "version": "0.1.0"},
                "capabilities": {"resources": {}, "tools": {}, "prompts": {}},
            },
        }
        self._jsonrpc_id_counter += 1

        for attempt in range(self.max_retries):
            try:
                response = await self._send_request_internal(initialize_request)

                if "error" in response:
                    raise ConnectionError(f"Failed to initialize: {response['error']}")

                # FIXED: Remove empty params from initialized notification
                notification: Dict[str, Any] = {
                    "jsonrpc": "2.0",
                    "method": "initialized",
                }
                await self._send_notification_internal(notification)

                self._logger.info("MCP protocol initialized successfully")
                return

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(
                        f"Failed to initialize after {self.max_retries} attempts: {e}"
                    )

                delay = self.retry_delay_s * (2**attempt)
                self._logger.warning(
                    f"Initialization attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)

    async def cleanup_async(self) -> None:
        """Clean up resources with proper session termination."""
        async with self._connection_lock:
            self._logger.info(f"Cleaning up connection to: {self.server_url}")

            if self._session_id and self._client and not self._client.closed:
                await self._terminate_session()

            await self._cleanup_client()
            await self.session_manager.close()

            self._session_id = None
            self._last_event_id = None
            self._initialized = False

    async def _cleanup_client(self) -> None:
        """Clean up HTTP client resources."""
        if self._client and not self._client.closed:
            await self._client.close()
        self._client = None

    async def _terminate_session(self) -> None:
        """Terminate session with the server."""
        if not self._session_id or not self._client:
            return

        try:
            headers: Dict[str, str] = {"Mcp-Session-Id": self._session_id}
            endpoint = (
                self.mcp_endpoint()
                if callable(self.mcp_endpoint)
                else self.mcp_endpoint
            )
            timeout = ClientTimeout(total=5.0)

            async with self._client.delete(
                endpoint, headers=headers, timeout=timeout, allow_redirects=True
            ) as response:
                response.raise_for_status()
                self._logger.debug(f"Session terminated: {self._session_id}")

            await self.session_manager.delete_session(self._server_key)

        except aiohttp.ClientError as e:
            self._logger.warning(f"Failed to terminate session: {e}")
        except Exception as e:
            self._logger.warning(
                f"An unexpected error occurred during session termination: {e}"
            )

    async def _store_session_data(self) -> None:
        """Store session data with error handling."""
        try:
            session_data = {
                "session_id": self._session_id,
                "last_event_id": self._last_event_id,
                "jsonrpc_counter": self._jsonrpc_id_counter,
            }
            await self.session_manager.store_session(self._server_key, session_data)
        except Exception as e:
            self._logger.warning(f"Failed to store session data: {e}")

    async def _send_request_internal(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Internal request sending with proper error handling."""
        if not self._client or self._client.closed:
            raise ConnectionError("Client not connected")

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        endpoint = (
            self.mcp_endpoint() if callable(self.mcp_endpoint) else self.mcp_endpoint
        )

        try:
            async with self._client.post(
                endpoint, json=request, headers=headers, allow_redirects=True
            ) as response:
                session_id = response.headers.get("Mcp-Session-Id")
                if session_id and session_id != self._session_id:
                    self._session_id = session_id
                    await self._store_session_data()

                if response.status == 404 and self._session_id:
                    self._logger.warning("Session expired, reconnecting...")
                    self._session_id = None
                    self._initialized = False
                    await self.session_manager.delete_session(self._server_key)
                    raise ConnectionError("Session expired")

                elif response.status != 200:
                    error_text = await response.text()
                    raise ConnectionError(f"HTTP {response.status}: {error_text}")

                content_type = response.headers.get("Content-Type", "")

                if "text/event-stream" in content_type:
                    request_id = request.get("id")
                    async for event in self._parse_sse_stream(response):
                        data = event["data"]
                        if isinstance(data, dict) and data.get("id") == request_id:
                            if "error" in data:
                                raise ValueError(f"JSON-RPC error: {data['error']}")
                            return data
                    raise ValueError("No matching response in SSE stream")

                elif "application/json" in content_type:
                    data = await response.json()
                    if "error" in data:
                        raise ValueError(f"JSON-RPC error: {data['error']}")
                    return data

                else:
                    raise ValueError(f"Unexpected content type: {content_type}")
        except aiohttp.ClientError as e:
            raise ConnectionError(f"AIOHTTP Client Error: {e}")

    async def _send_notification_internal(self, notification: Dict[str, Any]) -> None:
        """Internal notification sending."""
        if not self._client or self._client.closed:
            raise ConnectionError("Client not connected")

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        endpoint = (
            self.mcp_endpoint() if callable(self.mcp_endpoint) else self.mcp_endpoint
        )
        try:
            async with self._client.post(
                endpoint, json=notification, headers=headers, allow_redirects=True
            ) as response:
                response.raise_for_status()
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Failed to send notification: {e}")

    async def _send_request(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send request with retry logic and connection management."""
        if not self._is_connected():
            await self.connect_async()

        if not self._is_connected():
            raise ConnectionError("Failed to establish connection")

        request_id = str(self._jsonrpc_id_counter)
        self._jsonrpc_id_counter += 1

        # FIXED: Build request - only include params if they exist and are not empty
        request: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }

        # Only add params if they exist and are not empty
        if params:
            request["params"] = params

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                await self._store_session_data()
                return await self._send_request_internal(request)

            except ConnectionError as e:
                last_exception = e
                if "Session expired" in str(e):
                    await self.connect_async()
                    continue
                elif attempt == self.max_retries - 1:
                    break

                delay = self.retry_delay_s * (2**attempt)
                self._logger.warning(
                    f"Request attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)

            except Exception as e:
                self._logger.error(f"Request failed with non-recoverable error: {e}")
                raise

        raise last_exception or ConnectionError("Request failed after all retries")

    async def _parse_sse_stream(
        self, response: aiohttp.ClientResponse
    ) -> AsyncIterator[Dict[str, Any]]:
        """Parse SSE stream from an aiohttp response."""
        event_data = ""
        event_id = None
        event_type = None
        buffer = ""

        # aiohttp streams bytes, so we decode them and handle line breaks
        async for chunk in response.content.iter_any():
            buffer += chunk.decode("utf-8", "replace")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.rstrip("\r")

                if not line:
                    if event_data:
                        event_data = event_data.rstrip("\n")
                        try:
                            data = json.loads(event_data)
                            yield {
                                "id": event_id,
                                "type": event_type or "message",
                                "data": data,
                            }
                            if event_id:
                                self._last_event_id = event_id
                                await self._store_session_data()
                        except json.JSONDecodeError:
                            yield {
                                "id": event_id,
                                "type": event_type or "message",
                                "data": event_data,
                            }

                        event_data = ""
                        event_id = None
                        event_type = None
                    continue

                if line.startswith(":"):
                    continue

                match = re.match(r"([^:]+)(?::(.*))?", line)
                if match:
                    field, value = match.groups()
                    value = value.lstrip() if value else ""

                    if field == "data":
                        event_data += value + "\n"
                    elif field == "id":
                        event_id = value
                    elif field == "event":
                        event_type = value

    # MCP Protocol methods with proper error handling
    async def list_tools_async(self) -> Sequence[Tool]:
        """List tools with error handling."""
        from mcp.types import Tool

        try:
            response = await self._send_request("tools/list")
            if "result" not in response or "tools" not in response["result"]:
                raise ValueError("Invalid response format")
            return [Tool.model_validate(tool) for tool in response["result"]["tools"]]
        except Exception as e:
            self._logger.error(f"Failed to list tools: {e}")
            raise

    async def list_resources_async(self) -> Sequence[Resource]:
        """List resources with error handling."""
        from mcp.types import Resource

        try:
            response = await self._send_request("resources/list")
            if "result" not in response or "resources" not in response["result"]:
                raise ValueError("Invalid response format")
            return [
                Resource.model_validate(resource)
                for resource in response["result"]["resources"]
            ]
        except Exception as e:
            self._logger.error(f"Failed to list resources: {e}")
            raise

    async def list_resource_contents_async(
        self, uri: str
    ) -> Sequence[TextResourceContents | BlobResourceContents]:
        """List resource contents with error handling."""
        from mcp.types import BlobResourceContents, TextResourceContents

        try:
            response = await self._send_request("resources/read", {"uri": uri})
            if "result" not in response or "contents" not in response["result"]:
                raise ValueError("Invalid response format")

            return [
                TextResourceContents.model_validate(content)
                if content["type"] == "text"
                else BlobResourceContents.model_validate(content)
                for content in response["result"]["contents"]
            ]
        except Exception as e:
            self._logger.error(f"Failed to read resource {uri}: {e}")
            raise

    async def call_tool_async(
        self, tool_name: str, arguments: MutableMapping[str, object] | None
    ) -> CallToolResult:
        """Call tool with error handling."""
        from mcp.types import CallToolResult

        try:
            response = await self._send_request(
                "tools/call", {"name": tool_name, "arguments": arguments or {}}
            )
            if "result" not in response:
                raise ValueError("Invalid response format")
            return CallToolResult.model_validate(response["result"])
        except Exception as e:
            self._logger.error(f"Failed to call tool {tool_name}: {e}")
            raise
