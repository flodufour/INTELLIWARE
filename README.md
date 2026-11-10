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

Orion-LD answers on http://localhost:1026. Services are placeholders until implemented.

## Tracking

- [Project board](https://github.com/users/flodufour/projects/4)
- [Milestones](https://github.com/flodufour/INTELLIWARE/milestones)
