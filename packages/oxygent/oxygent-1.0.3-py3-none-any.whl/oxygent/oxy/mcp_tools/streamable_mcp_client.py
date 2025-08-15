"""Streamable-HTTP MCP client implementation."""

import logging
from typing import Any, Dict, List

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic import AnyUrl, Field

from ...utils.common_utils import build_url
from .base_mcp_client import BaseMCPClient

logger = logging.getLogger(__name__)


class StreamableMCPClient(BaseMCPClient):
    """MCP client implementation using Streamable-HTTP transport."""

    server_url: AnyUrl = Field("")
    headers: Dict[str, str] = Field(
        default_factory=dict, description="Extra HTTP headers"
    )
    middlewares: List[Any] = Field(
        default_factory=list, description="Client-side MCP middlewares"
    )

    async def init(self) -> None:
        """Initialize the HTTP streaming connection to the MCP server."""
        try:
            self._http_transport = await self._exit_stack.enter_async_context(
                streamablehttp_client(build_url(self.server_url), headers=self.headers)
            )
            read, write, _ = self._http_transport

            self._session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )

            for mw in self.middlewares:
                if hasattr(self._session, "add_middleware"):
                    self._session.add_middleware(mw)
                else:
                    logger.warning("middleware %s is ignored", mw)

            await self._session.initialize()
            await self.list_tools()
        except Exception as e:
            logger.error("Error initializing server %s: %s", self.name, e)
            await self.cleanup()
            raise Exception(f"Server {self.name} error") from e
