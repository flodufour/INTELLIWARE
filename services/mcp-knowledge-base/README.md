# MCP knowledge base

MCP server exposing the knowledge base to the agent.

Owner: Adrien. Placeholder until implemented.

Compose supplies the connection settings for the future server:

| Variable | Value in Compose |
|----------|------------------|
| `NEO4J_URI` | `bolt://neo4j:7687` |
| `NEO4J_USERNAME` | `neo4j` |
| `NEO4J_PASSWORD` | From `.env`, default `intelliware-dev` for local development |

The service waits for Neo4j's health check. See the root README for the
vector-index check and persistent volume. The placeholder does not query
Neo4j yet; the MCP tools remain those in `contracts/mcp/README.md`.
