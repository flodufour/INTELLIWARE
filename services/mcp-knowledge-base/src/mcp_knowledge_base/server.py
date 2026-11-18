"""First real knowledge-base MCP tool (issue #50)."""

import os
from contextlib import asynccontextmanager

from intelliware_mcp_contracts.models import PartInfo, fail
from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import DriverError, Neo4jError

from mcp_knowledge_base.knowledge import KnowledgeBase, UnknownPart


def create_server(*, repository=None, uri: str | None = None) -> MCPServer:
    backend = repository

    @asynccontextmanager
    async def lifespan(_):
        nonlocal backend
        if repository is not None:
            yield
            return
        auth = (os.environ.get("NEO4J_USERNAME", "neo4j"),
                os.environ.get("NEO4J_PASSWORD", "intelliware-dev"))
        async with AsyncGraphDatabase.driver(
            uri or os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687"), auth=auth,
            connection_timeout=5, max_transaction_retry_time=5,
        ) as driver:
            backend = KnowledgeBase(driver, os.environ.get("NEO4J_DATABASE", "neo4j"))
            try:
                yield
            finally:
                backend = None

    server = MCPServer("knowledge-base", instructions=(
        "OpenROV part metadata from the BOM graph. Null storage limits are unknown; "
        "do not infer safe storage conditions from missing limits."
    ), lifespan=lifespan)

    @server.tool(annotations=ToolAnnotations(read_only_hint=True, destructive_hint=False))
    async def get_part_info(part: str) -> PartInfo:
        """Read a part's BOM position, references and known storage limits."""
        if not part or part != part.strip():
            return fail("invalid_argument", "part must be a nonempty part type key")
        try:
            return await backend.get_part_info(part)
        except UnknownPart:
            return fail("not_found", f"unknown part '{part}'")
        except (Neo4jError, DriverError, ValueError, KeyError, TypeError):
            return fail("unavailable", "Neo4j is unavailable or returned invalid part data")

    return server


def main() -> None:
    port = int(os.environ.get("PORT", "8002"))
    hosts = os.environ.get("MCP_ALLOWED_HOSTS", f"localhost:{port},127.0.0.1:{port},mcp-knowledge-base:{port}")
    security = TransportSecuritySettings(
        allowed_hosts=[host.strip() for host in hosts.split(",") if host.strip()],
        allowed_origins=[f"http://localhost:{port}", f"http://127.0.0.1:{port}"],
    )
    create_server().run("streamable-http", host=os.environ.get("HOST", "127.0.0.1"),
                        port=port, transport_security=security)
