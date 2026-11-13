# INTELLIWARE
A one-shelf smart warehouse for an underwater vehicle: a PIPER arm stores and retrieves spare parts, a digital twin knows what is where, and an AI agent answers technicians in French or English. ESILV A4 project, 2026-27.

Documentation site: https://flodufour.github.io/INTELLIWARE/

## Documents

- [Genesis](project_definition/genesis.md): team, origin, vision
- [Scope](project_definition/scope.md): what we build and with which technologies
- [Roadmap](project_definition/roadmap.md): sprints, dates, way of working
- [Material](project_definition/material.md): hardware needed, source and status
- [Architecture](project_definition/architecture.html): one-page view of the blocks
- [Contributing](CONTRIBUTING.md): git conventions

## Repository structure

```
contracts/        Interfaces between blocks: MCP tools, NGSI-LD model, robot command
services/         One folder and one Docker service per block
  interface/  agent/  mcp-twin/  mcp-knowledge-base/  mcp-robot/
  simulator/  vision/  robot/
data/             OpenROV files (original license) and our procedures
hardware/         Our CAD (SolidWorks, STEP, STL): shelf, tray, mounts
tests/e2e/        End-to-end scenarios on the full chain
project_definition/
docker-compose.yml        Main machine: twin, services, agent, interface
docker-compose.robot.yml  Robot machine: robot and vision
```

Each service has the same layout: `Dockerfile`, `pyproject.toml`, `src/<package>/`, `tests/`.

## Run

Requires Docker Desktop.

```
docker compose up -d --build                             # main machine
docker compose -f docker-compose.robot.yml up -d --build  # robot machine
docker compose ps                                        # check services
docker compose down                                      # stop
```

Orion-LD answers on http://localhost:1026. Neo4j Browser is at
http://localhost:7474 and Bolt at `bolt://localhost:7687`. Services are
placeholders until implemented.

### Neo4j

Neo4j Community 5.26 LTS stores the knowledge graph and document vectors.
Vector indexes are built in; no plugin or Enterprise license is needed.
The `neo4j-data` volume persists the database when containers are recreated.
`docker compose down` keeps it; `docker compose down --volumes` deletes the data.

Local development credentials are `neo4j` / `intelliware-dev`. Copy
[.env.example](.env.example) to `.env` to override the password before the
first start. An existing volume keeps its credentials when `.env` changes.
The published Neo4j ports accept connections only from this machine.

```sh
docker compose up -d --wait neo4j
python scripts/check_neo4j.py
```

For a custom password, also set `NEO4J_PASSWORD` in the shell running the
Python check (PowerShell: `$env:NEO4J_PASSWORD = 'your-password'`). It uses the
HTTP Query API, creates a temporary 3-dimensional vector index, waits until
it is online, checks the nearest neighbor and removes its test data. The
`neo4j-vector` CI job runs the same check on every PR. These synthetic vectors
only validate database support; the multilingual embedding model and the
document index will be added with ingestion in sprint 2.

Inside Compose, `mcp-knowledge-base` connects to `bolt://neo4j:7687` and starts
after Neo4j is healthy. Orion-LD and MongoDB remain the live digital twin;
Neo4j holds the BOM and documentation. Part keys (`propeller`, `cap`, `clip`)
and `bomRef` must match the NGSI-LD contract when ingestion is implemented.

## Tracking

- [Project board](https://github.com/users/flodufour/projects/4)
- [Milestones](https://github.com/flodufour/INTELLIWARE/milestones)
