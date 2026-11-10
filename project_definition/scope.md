# INTELLIWARE - Project Scope

What we build and with which technologies. Source of truth: where [genesis.md](genesis.md) differs, this document wins. Schedule in [roadmap.md](roadmap.md).

## Goal

A smart spare parts warehouse for an underwater vehicle, reduced to **one shelf**. A robot arm stores and retrieves parts, a digital twin knows at all times what is where, and an AI agent answers technicians in French or English, linking each part to its documentation.

## Reference product

**OpenROV**, an open-source underwater vehicle (fallback: an open-source 3D-printed RC submarine).

- Its public BOM and documentation (English) feed the knowledge base. We write the maintenance procedures (French) and the stock levels.
- Small 3D-printed or laser-cut parts of the vehicle are the physical spare parts.

## Physical setup

- Two PIPER arms: a leader moved by hand for teleoperation, a follower working on the shelf.
- One shelf: 2 levels, 4 to 6 slots, 3 to 4 part types, within reach of the follower arm.
- One input/output tray.
- A fixed RGB-D camera facing the shelf and a wrist camera on the gripper.

Full hardware list and status in [material.md](material.md).

## Scenarios

| Scenario | What happens |
|----------|--------------|
| Diagnose | "The thruster vibrates, what should I check?" The knowledge base gives the procedure and the parts involved (BOM graph), the twin gives their stock. The agent can chain to Retrieve. No robot move. |
| Store | A part is put on the tray. Vision identifies it, the twin assigns a free slot, the robot stores it. |
| Retrieve | "I need a spare thruster propeller." The agent gives the location and the replacement procedure. After confirmation, the robot brings the part to the tray. |
| Replenish | Below its stock threshold, a part gets a purchase order with supplier and delivery date. On delivery, it goes through Store. |
| Inventory | After each task and on request, the fixed camera scans the shelf. Mismatches with the twin are flagged and corrected. |
| Monitor | A simulated sensor crosses its threshold (e.g. shelf humidity). The knowledge base gives the storage conditions of the parts at risk, the agent alerts the technician, the alert is traced in the twin. |
| Failures | Dropped part: detected and retried. Missing part: the robot stops, the twin is corrected, the technician is informed. |

Every physical action is confirmed by a human and traced in the twin.

## Scope

| In scope | Out of scope | Stretch goals |
|----------|--------------|---------------|
| One shelf, one robot, one tray | Several shelves or robots | Second shelf |
| Digital twin with simulated sensors (temperature, humidity) | Physical IoT sensors | Slot weight sensors, 3D view |
| Simulated supply chain: thresholds, purchase orders, lead times | ERP or supplier integration | |
| Text chat in French and English | Other languages | Voice interface |
| LLM through a school API key, otherwise local (Ollama) | | |
| Inference on a laptop GPU | | Jetson deployment |

## Building blocks

| Block | Role | Technologies |
|-------|------|--------------|
| Interface | Chat, action confirmation, live shelf view | Streamlit |
| Agent | Understands requests, calls tools, asks for confirmation, answers in the user's language | Pydantic AI, LLM via school API key or local Ollama |
| Digital twin | Live state of shelf, slots, parts, robot, sensors, purchase orders, task history | FIWARE Orion-LD (NGSI-LD), MongoDB |
| Knowledge base | BOM as a graph, manuals, procedures and standards as searchable chunks | Neo4j (graph + vector index), multilingual embeddings |
| MCP servers | Expose twin, knowledge base and robot to the agent as tools | Python MCP SDK |
| Simulator | Sensor values, purchase orders, deliveries | Python, NGSI-LD API |
| Robot | Leader-follower teleoperation, recording, store and retrieve gestures | PIPER arm, ROS 2, LeRobot, SmolVLA |
| Vision | Identifies parts, checks grasp success, scans the shelf | YOLO-World |
| Infrastructure | Same setup on every machine, automated tests | Docker Compose, GitHub Actions |

All code in Python.

## Architecture principles

Every block can be developed, run and tested alone.

- **Three contracts**, agreed in sprint 0, changed only through a PR reviewed by both sides:
  - MCP tools: agent to twin, knowledge base and robot.
  - NGSI-LD entities: everything stored in the twin.
  - Robot command format: robot MCP server to robot controller.
- **One Docker Compose service per block**, with a mock of its contract so neighbors can work without it.
- **The agent knows tools, not implementations**: swapping a mock for the real block changes nothing in the agent.

| Block | Tested alone with |
|-------|-------------------|
| Interface | Mock agent with scripted answers |
| Agent | Mock MCP tools, scripted scenarios in French and English |
| Knowledge base | RAG question set, scored automatically |
| Digital twin | Create, update, query and subscription tests on Orion-LD |
| Simulator | Scripted runs on a test twin |
| MCP servers | Tool calls on a test twin and test knowledge base |
| Vision | Labeled images of the shelf |
| Robot | Bench trials on fixed commands |

End-to-end tests run the scenarios on the full chain from the walking skeleton (Dec 11, 2026) onward.

## Technology choices

- **The twin is the single source of truth** for what is where, updated by every robot action and every scan.
- **SmolVLA rather than OpenVLA**: small enough to fine-tune with LoRA on one GPU and to run on a laptop GPU. Fallbacks: ACT, then a detector-guided scripted grasp. The VLA stays a deliverable (trained, evaluated, reported) even if a fallback runs the live demo.
- **Vision separate from the VLA**: a VLA does not report failure; the detector says whether a part is in its slot, in the gripper or dropped.
- **Fixed-format robot instructions**: the agent turns any request, French or English, into one English instruction ("pick the propeller from slot B2"). Consistent dataset, same action in both languages.
- **Neo4j for hybrid RAG**: graph and vector search in one database.
- **LLM provider open**: a hosted API (Claude or OpenAI) if the school provides keys, otherwise a local model via Ollama. Pydantic AI makes switching a configuration change; the agent test scenarios decide whether a local model is good enough.

## Compute

- **Training**: one GPU with at least 12 GB VRAM (team, school or cloud). Team GPUs run separate experiments in parallel; one training split across PCs would be slower.
- **Inference**: laptop GPU next to the robot (Florian: RTX 3050 Laptop, 4 GB, enough for the detector and probably SmolVLA). Jetson later if time allows.

## Compliance with proposals 7 and 10

| Requirement | How we meet it |
|-------------|----------------|
| P7 - Master-slave teleoperation with RGB-D feedback | ROS 2 leader-follower teleoperation and recording |
| P7 - Imitation dataset: trajectories, video, instructions | Store and retrieve demonstrations |
| P7 - VLA fine-tuning via LoRA | SmolVLA with LoRA |
| P7 - Embedded deployment (Jetson type) | **Partial**: PC first, Jetson (being ordered) if time allows |
| P7 - Robustness to lighting and target displacement | Success criteria below |
| P7 - Physical demo on command, with success rate | Text command, success criteria below |
| P7 - Construction finishing (application domain) | **Changed**: warehouse handling, same skills |
| P10 - Hybrid RAG, graph and vector | Neo4j |
| P10 - Context Broker with inventory and sensors | Orion-LD: inventory by vision, simulated sensors |
| P10 - MCP server to query FIWARE | Built by us |
| P10 - Chat for technical and logistic queries | Procedure, location and supply status in one answer |
| P10 - Real-time supply chain status | Simulated purchase orders and lead times |
| P10 - Multilingual manuals and standards | English documentation, French procedures, both languages in chat |
| P10 - Naval context | Underwater vehicle |

Both deviations (Jetson, domain) approved by the supervisors on Nov 10, 2026.

## Team workstreams

| Member | Workstream |
|--------|------------|
| Florian (lead) | Digital twin, simulator, robot hardware and ROS 2, repository structure, integration |
| Adrien | Knowledge base, twin and knowledge base MCP servers, CI |
| Antoine | Reference product data, shelf, vision, safety rules, tests and metrics |
| Louis-Marie | Agent, interface, robot MCP server, VLA training |

Everyone records robot demonstrations.

## Milestones

Deadline: **March 1, 2027**, set by the team to finish before the end-of-year exams, with one to two weeks of margin. Sprints in [roadmap.md](roadmap.md).

| Date | Milestone | Done when |
|------|-----------|-----------|
| Nov 13, 2026 | Kickoff | Scope approved, contracts and mocks agreed, hardware confirmed |
| Dec 11, 2026 | Walking skeleton | Chat to agent to twin, knowledge base and scripted robot move; simulator feeds the twin |
| Jan 15, 2027 | First model | Demonstrations recorded, SmolVLA trained, vision detects presence and grasp state |
| Jan 29, 2027 | VLA go/no-go | VLA kept for the demo, or replaced by a fallback; VLA results reported either way |
| Feb 12, 2027 | Feature freeze | All scenarios end to end, robustness tests done |
| Mar 1, 2027 | Delivery | Validation report, demo, defense |

## Success criteria

Targets confirmed after the first tests.

- Store and retrieve: at least 80% success over 20 trials each, kept under lighting changes and shifted parts.
- The twin matches the shelf after every task and scan; manual changes caught at the next scan.
- A missing part is always reported.
- Every sensor threshold crossing raises an alert.
- RAG: at least 85% correct answers on the question set, in French and in English.
- The same request in French or English gives the same robot action.
- 100% of physical actions confirmed and traced.

## Main risks

| Risk | Mitigation |
|------|------------|
| Four months is short for robot learning | Small shelf, full pipeline tested on one slot by Dec 11, go/no-go on Jan 29, fallbacks ready |
| Incomplete OpenROV data | Checked in sprint 0; complete it ourselves or switch product |
| Slots out of reach | Shelf designed around the PIPER workspace, open-top bins |
| PIPER not supported by LeRobot | Checked in sprint 0; adapter on top of the ROS 2 driver |
| No 12 GB GPU | School or cloud GPU |
| Late or broken integration | Contracts in sprint 0, walking skeleton Dec 11, end-to-end tests after |

## Open questions

- LLM: API keys from the school, or local Ollama.
- Training GPU: access to school GPUs, or GPUs of Adrien, Antoine and Louis-Marie (`nvidia-smi`). Remaining hardware in [material.md](material.md).
- Which vehicle parts go on the shelf.
