# MCP knowledge base

MCP server exposing the knowledge base to the agent.

Owner: Adrien. BOM ingestion is implemented; the MCP entry point remains a
placeholder until issue #50.

Compose supplies the connection settings for the future server:

| Variable | Value in Compose |
|----------|------------------|
| `NEO4J_URI` | `bolt://neo4j:7687` |
| `NEO4J_USERNAME` | `neo4j` |
| `NEO4J_PASSWORD` | From `.env`, default `intelliware-dev` for local development |

The service waits for Neo4j's health check. See the root README for the
vector-index check and persistent volume. The MCP tools remain those in
`contracts/mcp/README.md`.

## Import the mechanical BOM

The input is `data/openrov/derived/bom.csv`, defined in PR #41. Merge that
data PR before using the default path. The importer also accepts another
CSV path with the same seven columns. No upstream data is copied into the
importer or its synthetic test fixtures.

From the repository root, with Python 3.12 and a virtual environment:

```sh
python -m pip install -e services/mcp-knowledge-base
docker compose up -d --wait neo4j
python -m mcp_knowledge_base.bom
# Or: python -m mcp_knowledge_base.bom path/to/bom.csv
```

On the host, `NEO4J_URI` defaults to `bolt://127.0.0.1:7687`. Set
`NEO4J_USERNAME`, `NEO4J_PASSWORD` and optionally `NEO4J_DATABASE` for another
instance (database default: `neo4j`). As with the vector check, export a custom
password in the calling shell; `.env` is read by Compose, not by Python.

The importer validates the complete UTF-8 CSV before writing: exact header,
nonempty fields, positive integer quantities and unique `part_id` / `bom_ref`.
Uniqueness constraints protect the identifiers in Neo4j. All data rows are
written in one transaction; a database conflict rolls back that import.

## Graph

```text
(:Assembly {assembly_id: "OR28"})-[:HAS_PART {quantity: 2}]->
(:PartType {part_id: "collar", bom_ref: "OR28-COLLAR", name_en: ..., name_fr: ..., source_url: ...})
```

- `PartType.part_id` is the MCP `part` and the key of the NGSI-LD PartType URN.
- `PartType.bom_ref` is the twin's `bomRef`; bilingual names are kept separately.
- `Assembly.assembly_id` comes from `parent_assembly`. The source CSV is flat:
  it lists the whole vehicle `OR28`, not immediate CAD subassemblies.
- `HAS_PART.quantity` is the occurrence count in that assembly, not shelf stock.
  Live stock remains in Orion-LD.

Re-running the same input reuses nodes and relationships. Changed names,
references, sources and counts are updated rather than incremented. Other
properties and relationships (documents, procedures, storage information)
are preserved. This is an upsert: rows omitted from a later CSV are not pruned.

Example query for the selected types after the full CSV import:

```cypher
MATCH (a:Assembly {assembly_id: 'OR28'})-[r:HAS_PART]->(p:PartType)
WHERE p.part_id IN ['endcap', 'collar', 'twist-lock']
RETURN p.part_id, p.bom_ref, p.name_fr, r.quantity
ORDER BY p.part_id;
```

## Tests

Install `requirements-dev.txt` as well as the service package, then run
`python -m pytest services/mcp-knowledge-base/tests`. CSV tests run without
Neo4j. Database tests are opt-in and use unique fixture IDs, cleaning up only
their own nodes. With a dedicated local test instance:

```powershell
$env:NEO4J_TEST_URI = 'bolt://127.0.0.1:7687'
python -m pytest -m neo4j services/mcp-knowledge-base/tests
```

On Linux/macOS, prefix the pytest command with `NEO4J_TEST_URI=bolt://127.0.0.1:7687`.
The `neo4j-vector` CI job runs these integration tests against an isolated
Neo4j service: repeated imports, metadata updates, preservation of unrelated
knowledge, invalid input and transaction rollback.
