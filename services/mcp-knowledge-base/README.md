# MCP knowledge base

MCP server exposing the knowledge base to the agent.

Owner: Adrien. `get_part_info` reads the Neo4j BOM graph. Document search
and procedure retrieval remain in the mock until their implementation sprint.

Compose supplies the connection settings:

| Variable | Value in Compose |
|----------|------------------|
| `NEO4J_URI` | `bolt://neo4j:7687` |
| `NEO4J_USERNAME` | `neo4j` |
| `NEO4J_PASSWORD` | From `.env`, default `intelliware-dev` for local development |

The service waits for Neo4j's health check. See the root README for the
vector-index check and persistent volume. The tool uses the shared models in
`contracts/mcp/README.md`.

## Run the server

```sh
docker compose up -d --build --wait neo4j mcp-knowledge-base
```

The Streamable HTTP endpoint is `http://127.0.0.1:8002/mcp` on the host and
`http://mcp-knowledge-base:8002/mcp` inside Compose. The published port is local
to the machine. For Python development:

```sh
python -m pip install -e contracts/mcp -e services/mcp-knowledge-base
python -m mcp_knowledge_base
```

On the host, `NEO4J_URI` defaults to `bolt://127.0.0.1:7687`, `NEO4J_DATABASE`
to `neo4j`, `HOST` to `127.0.0.1`, and `PORT` to `8002`. Compose supplies its
internal database URL. A comma-separated `MCP_ALLOWED_HOSTS` override supports
other deployments while keeping DNS-rebinding protection enabled.

## Part metadata

Load the BOM with the importer from PR #62 (issue #48), after merging the data
PR #41. This tool reads that graph; it does not copy CSV data into the service.

- `PartType.part_id` maps to MCP `part`; `name_en` / `name_fr` to `names`.
- Incoming `(:Assembly)-[:HAS_PART]->(p)` gives the parent assembly. Missing
  parents give `null`; multiple distinct parents give `unavailable` rather
  than selecting an arbitrary parent for the contract's singular field.
- Outgoing `HAS_PART` to PartType, undirected `RELATED_TO`, `HAS_PROCEDURE` to
  Procedure (`procedure_id`) and `DOCUMENTED_IN` to Document (`document`, with
  `section` on the relationship) supply optional metadata. Missing links give
  empty lists; shared membership in OR28 is not a maintenance relationship.
- The part's `source_url` is returned as a source document reference, with an
  empty section when none is specified.
- `storage_temperature_min`, `storage_temperature_max`, `storage_humidity_max`
  are recorded numeric conditions. Missing values remain `null`: the BOM
  contains no such conditions. Unknown does not mean unrestricted; Monitor
  must report missing conditions instead of inventing a threshold.

Unknown parts give `not_found`, empty keys `invalid_argument`, and backend
failures or invalid graph data `unavailable`. All Cypher uses parameters.
The server makes no inventory, schema or graph writes. Vector search and
procedure ingestion are still planned for sprint 2.

## Tests

`python -m pytest services/mcp-knowledge-base/tests` runs mapping and MCP
protocol tests without Neo4j. The `knowledge` tests opt into a dedicated
database with `NEO4J_TEST_URI`; `MCP_KNOWLEDGE_BASE_TEST_URL` additionally
tests the deployed HTTP endpoint. Fixtures use unique IDs and clean up only
their own nodes. The `knowledge-live` workflow runs the full integration path.
