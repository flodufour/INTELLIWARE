# mcp

MCP tools the agent uses, exposed by three servers: twin, knowledge base, robot. Issue #15.

The agent knows these tools and nothing else. A mock of each server is in this folder; swapping a mock for the real server changes nothing in the agent.

| Server | Service | Owner | Port | Mock |
|--------|---------|-------|------|------|
| Twin | `mcp-twin` | Adrien | 8001 | [mock_twin.py](mock_twin.py) |
| Knowledge base | `mcp-knowledge-base` | Adrien | 8002 | [mock_knowledge_base.py](mock_knowledge_base.py) |
| Robot | `mcp-robot` | Louis-Marie | 8003 | [mock_robot.py](mock_robot.py) |

## Conventions

- **Transport**: streamable HTTP at `http://<service>:<port>/mcp`. The agent reads the URLs from `MCP_TWIN_URL`, `MCP_KNOWLEDGE_BASE_URL`, `MCP_ROBOT_URL`.
- **Ids** are shared by every block:
  - `part`: part type id, lowercase English, e.g. `propeller`. Same id in the twin, the BOM graph and the robot instruction.
  - `slot`: level letter and position, e.g. `A1`, `B2`. Same as [robot-command](../robot-command/).
  - Final ids come from the NGSI-LD model (#8) and the part list (#13).
- **Language**: tools return data, not prose. Names come in both languages (`names: {"en": ..., "fr": ...}`); documents in their original language. The agent answers in the user's language.
- **Outputs** are JSON objects (MCP structured content). Times are ISO 8601 UTC. The output types below are Pydantic models in [models.py](models.py); a tool annotated with its model publishes the JSON schema to the agent. Real servers import them.
- **Errors**: the tool result has `isError: true` and its text is `{"error": "<code>", "message": "<English text>"}`. Use `models.fail()`: a raised exception gets an SDK prefix and is no longer plain JSON. Codes used by every tool:

| Code | Meaning |
|------|---------|
| `invalid_argument` | Bad input, e.g. malformed slot |
| `not_found` | Unknown part, slot, procedure or alert |
| `unavailable` | Backend down (Orion-LD, Neo4j, robot controller) |

Tool-specific codes are listed with each tool.

## Twin server

Reads the live state of the shelf from Orion-LD. The only write is `acknowledge_alert`; robot actions are written by the robot server.

| Tool | Inputs | Output | Errors |
|------|--------|--------|--------|
| `list_parts` | | `{parts: [Part]}` | |
| `get_part` | `part` | `Part` | `not_found` |
| `get_shelf` | | `{slots: [Slot], tray: {part: str \| null}}` | |
| `find_free_slot` | `part` | `{slot: str}` | `not_found`, `shelf_full` |
| `list_purchase_orders` | `part?`, `status?` (`ordered`, `delivered`) | `{orders: [PurchaseOrder]}` | `not_found` |
| `list_sensors` | | `{sensors: [Sensor]}` | |
| `list_alerts` | `active_only?` (default `true`) | `{alerts: [Alert]}` | |
| `acknowledge_alert` | `alert_id`, `by` | `Alert` | `not_found` |
| `list_tasks` | `limit?` (default 10) | `{tasks: [Task]}`, latest first | |

```
Part          {part, names: {en, fr}, stock: int, threshold: int, slots: [str]}
Slot          {slot, level: int, part: str | null}
PurchaseOrder {id, part, quantity, supplier, status: ordered | delivered, ordered_at, expected_at}
Sensor        {sensor, kind: temperature | humidity, value: float, unit, min: float | null, max: float | null, status: ok | alert, observed_at}
Alert         {id, sensor, kind, value, limit, raised_at, acknowledged_by: str | null, acknowledged_at}
Task          {task_id, action: store | retrieve | home, part, slot, status, failure, confirmed_by, started_at, finished_at}
```

`stock` counts parts on the shelf. Purchase orders are created by the simulator when stock falls below `threshold`; the agent only reads them.

## Knowledge base server

Searches the OpenROV documentation and our procedures in Neo4j.

| Tool | Inputs | Output | Errors |
|------|--------|--------|--------|
| `search_documents` | `query`, `limit?` (default 5) | `{chunks: [Chunk]}`, best first | |
| `get_procedure` | `procedure_id` | `Procedure` | `not_found` |
| `get_part_info` | `part` | `PartInfo` | `not_found` |

```
Chunk     {chunk_id, text, document, section, kind: manual | procedure | standard, language: en | fr, procedure_id: str | null, score: float}
Procedure {procedure_id, title, language, steps: [str], parts: [str], document}
PartInfo  {part, names: {en, fr}, assembly: str | null, subparts: [str], related_parts: [str],
           documents: [{document, section}], storage: {temperature_min, temperature_max, humidity_max}}
```

`query` can be French or English; the multilingual embeddings match both. `assembly` is the parent in the BOM graph, `related_parts` the parts usually replaced together.

## Robot server

Drives the arm through the [robot-command](../robot-command/) contract and vision. After every task and scan it writes the result to the twin (Task entity, slot contents).

Physical actions (`store_part`, `retrieve_part`) need a human confirmation: the agent asks in the interface first and passes who confirmed as `confirmed_by`. They block until the task ends and return its final status. A failed task is a normal result, not a tool error.

| Tool | Inputs | Output | Errors |
|------|--------|--------|--------|
| `identify_tray_part` | | `{part: str \| null, confidence: float}` | |
| `store_part` | `part`, `slot`, `confirmed_by` | `TaskResult` | `not_confirmed`, `robot_busy` |
| `retrieve_part` | `part`, `slot`, `confirmed_by` | `TaskResult` | `not_confirmed`, `robot_busy` |
| `scan_shelf` | | `{slots: [{slot, part: str \| null}], mismatches: [Mismatch]}` | `robot_busy` |
| `stop_robot` | | `{stopped_task_id: str \| null}` | |
| `get_robot_status` | | `{state: idle \| busy \| error, task_id: str \| null}` | |

```
TaskResult {task_id, status: succeeded | failed | stopped, failure: str | null, attempts: int, part_location: str | null, message}
Mismatch   {slot, twin: str | null, seen: str | null}
```

`failure` and `part_location` are those of [robot-command](../robot-command/#failures). `not_confirmed`: `confirmed_by` is empty. `scan_shelf` corrects the twin and returns what it changed in `mismatches`.

## Scenarios

| Scenario | Tool calls |
|----------|------------|
| Diagnose | `search_documents` -> `get_procedure` -> `get_part` for each part |
| Store | `identify_tray_part` -> `find_free_slot` -> confirm -> `store_part` |
| Retrieve | `get_part` -> `get_procedure` (replacement) -> confirm -> `retrieve_part` |
| Replenish | `get_part` -> `list_purchase_orders` |
| Inventory | `scan_shelf` |
| Monitor | `list_alerts` -> `list_sensors` -> `get_part_info` for parts on the shelf -> `acknowledge_alert` |

## Mocks

In-memory, with fixed data (placeholder parts `propeller`, `cap`, `clip` until #13). The three mocks do not share state. They need [uv](https://docs.astral.sh/uv/), which installs the MCP SDK (2.x) on first run.

```sh
uv run contracts/mcp/mock_twin.py            # :8001/mcp
uv run contracts/mcp/mock_knowledge_base.py  # :8002/mcp
uv run contracts/mcp/mock_robot.py           # :8003/mcp
```

Mock robot: tasks take 2 s and succeed, except slot `Z9` (`part_missing`) and part `broken` (`grasp_failed`).
