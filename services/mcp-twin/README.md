# MCP twin

MCP server exposing the digital twin to the agent.

Owner: Adrien. The first three tools read Orion-LD through the NGSI-LD contract:
`list_parts`, `get_part` and `get_shelf`. The other tools remain in the mock
until their implementation sprint.

## Run

```sh
docker compose up -d --build mongo orion-ld mcp-twin
python contracts/ngsi-ld/seed.py
```

Wait until Orion-LD answers on port 1026 before loading the seed. Seeding
replaces the contract entity types; use it only on a development instance.
The endpoint is `http://127.0.0.1:8001/mcp` on the host and
`http://mcp-twin:8001/mcp` for the agent on the Compose network.

For local Python development:

```sh
python -m pip install -e contracts/mcp -e services/mcp-twin
python -m mcp_twin
```

`ORION_URL` defaults to `http://127.0.0.1:1026`; `HOST` to `127.0.0.1` and
`PORT` to `8001`. Compose supplies the internal broker URL and binds the server
to its container interfaces; the published port stays local to the machine.
`MCP_ALLOWED_HOSTS` can override the comma-separated HTTP Host allowlist for
another deployment. DNS-rebinding protection remains enabled.

Stock is counted from Slot relationships on every call, never copied from
Neo4j or cached. An absent `refPartType` becomes `null` in slot/tray output.
Part and slot keys are read from URNs, so Florian's seed update in #47 does
not require hardcoded part names here. Unknown parts produce `not_found`,
empty part keys `invalid_argument`, and backend failures or invalid data
`unavailable`, using the shared error model.

## Tests

`python -m pytest services/mcp-twin/tests` runs protocol tests with controlled
HTTP responses. The `orion` integration test is enabled with
`ORION_TEST_URL` and `MCP_TWIN_TEST_URL`, against a dedicated seeded instance.
It calls the real Streamable HTTP endpoint, checks the shared models, then
temporarily clears and restores a slot relationship to verify live stock.
The `twin-live` CI job runs that test on isolated containers.
