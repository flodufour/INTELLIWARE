"""First real MCP tools of the digital twin (issue #49)."""

import os
from contextlib import asynccontextmanager

import httpx2
from intelliware_mcp_contracts.models import Part, Parts, Shelf, fail
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from mcp_twin.orion import Orion, UnknownPart


def create_server(orion_url: str | None = None, *, transport=None) -> MCPServer:
    backend = None

    @asynccontextmanager
    async def lifespan(_):
        nonlocal backend
        async with httpx2.AsyncClient(
            base_url=(orion_url or os.environ.get("ORION_URL", "http://127.0.0.1:1026")).rstrip("/"),
            timeout=5, transport=transport,
        ) as client:
            backend = Orion(client)
            try:
                yield
            finally:
                backend = None

    server = MCPServer("twin", instructions="Live shelf state from Orion-LD.", lifespan=lifespan)
    readonly = ToolAnnotations(read_only_hint=True, destructive_hint=False)

    @server.tool(annotations=readonly)
    async def list_parts() -> Parts:
        """List part types, live stock, thresholds and occupied slots."""
        try:
            return await backend.list_parts()
        except (httpx2.HTTPError, ValueError, KeyError, TypeError):
            return fail("unavailable", "Orion-LD is unavailable or returned invalid inventory data")

    @server.tool(annotations=readonly)
    async def get_part(part: str) -> Part:
        """Read one part type and calculate its stock from occupied slots."""
        if not part or part != part.strip():
            return fail("invalid_argument", "part must be a nonempty part type key")
        try:
            return await backend.get_part(part)
        except UnknownPart:
            return fail("not_found", f"unknown part '{part}'")
        except (httpx2.HTTPError, ValueError, KeyError, TypeError):
            return fail("unavailable", "Orion-LD is unavailable or returned invalid inventory data")

    @server.tool(annotations=readonly)
    async def get_shelf() -> Shelf:
        """Read slot contents and the input/output tray."""
        try:
            return await backend.get_shelf()
        except (httpx2.HTTPError, ValueError, KeyError, TypeError):
            return fail("unavailable", "Orion-LD is unavailable or returned invalid inventory data")

    return server


def main() -> None:
    port = int(os.environ.get("PORT", "8001"))
    hosts = os.environ.get("MCP_ALLOWED_HOSTS", f"localhost:{port},127.0.0.1:{port},mcp-twin:{port}")
    security = TransportSecuritySettings(
        allowed_hosts=[host.strip() for host in hosts.split(",") if host.strip()],
        allowed_origins=[f"http://localhost:{port}", f"http://127.0.0.1:{port}"],
    )
    create_server().run("streamable-http", host=os.environ.get("HOST", "127.0.0.1"),
                        port=port, transport_security=security)
