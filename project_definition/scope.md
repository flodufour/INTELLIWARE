# INTELLIWARE - Project Scope

What the project does, what it does not do, and which technologies we use. Builds on [genesis.md](genesis.md); where they differ, this document wins.

## Goal

A smart spare parts warehouse for a naval product, reduced to **one shelf**. A robot arm stores and retrieves parts. A mini digital twin knows at all times what is where. An AI agent lets a technician talk to the warehouse in natural language and links each part to its technical documentation.

## Reference product

An **open-source underwater vehicle**. Candidate: **OpenROV** (public BOM, electronics and mechanical files). Fallback: an open-source 3D-printed RC submarine.

- Real military submarine data is classified and out of the question.
- From the public files we take the BOM and the documentation (English). Maintenance procedures are written by us in French, and stock levels are created by us. The knowledge base is mixed-language by design.
- Small parts of the vehicle (3D printed or laser cut) are the physical spare parts the robot handles.

## Physical setup

- One small shelf (2 to 3 levels, 6 to 9 slots) within reach of the PIPER arm.
- One input/output tray where parts are dropped off and handed over.
- A fixed RGB-D camera facing the shelf (inventory) and a wrist camera (grasping).

## Scenarios

**Store.** A technician puts a part on the tray and says "store this". The robot identifies it with the camera, the twin assigns a free slot, the robot stores it, the twin is updated.

**Retrieve.** "I need a spare thruster propeller." The agent finds its slot in the twin and the replacement procedure in the knowledge base. The technician confirms. The robot picks the part and places it on the tray.

**Replenish.** When a part falls below its stock threshold, the twin creates a simulated purchase order with a supplier and an expected delivery date. The agent can answer "when will it arrive?". On delivery, the part goes through the Store scenario.

**Inventory.** After each task and on request, the fixed camera scans the shelf. The result is compared with the twin. Any mismatch (part moved or removed by hand) is flagged and corrected.

**Failures.**
- Part dropped: detected by vision, the robot retries.
- Part not in its slot: the robot stops, the twin is corrected, the agent informs the technician.

Every physical action requires human confirmation and is traced in the twin.

## Scope

| In scope | Out of scope | Stretch goals |
|----------|--------------|---------------|
| One shelf, one robot, one tray | Multiple shelves or robots | Second shelf |
| Mini digital twin: shelf, slots, parts, robot, tasks | Real employer or military data | 3D view of the twin |
| Simulated sensors in the twin (shelf temperature, humidity, slot weight) | Physical IoT sensors | Real weight sensors on slots |
| Store, retrieve, inventory scan | Autonomous action without validation | Voice interface |
| Simulated supply chain: stock thresholds, purchase orders, supplier lead times | Real ERP or supplier integration | |
| Vision-based grasp with drop and missing-part handling | | Local LLM in production |
| Text chat with live shelf view | | |
| Bilingual French / English: questions, answers, interface and documentation | Other languages | |

## Building blocks

| Block | What it does | Technologies |
|-------|--------------|--------------|
| Interface | Chat with the agent, action confirmation, live view of the shelf, in French or English | Streamlit |
| Agent | Understands requests, calls tools, asks for confirmation, answers in the user's language | Python, Pydantic AI, Claude API (local model via Ollama later) |
| Digital twin | Live state of shelf, slots, parts, robot, simulated sensors, purchase orders and task history | FIWARE Orion-LD (NGSI-LD) |
| Knowledge base | BOM as a graph, manuals, procedures and applicable standards as searchable chunks | Neo4j (graph + vector index), multilingual embedding model |
| MCP servers | Expose twin, knowledge base and robot to the agent as tools | Python MCP SDK, built by us |
| Robot control | Leader-follower teleoperation, recording, execution of store and retrieve gestures | PIPER arm, ROS 2, LeRobot, SmolVLA |
| Vision | Identifies parts, checks grasp success, scans the shelf | Open-vocabulary detector (YOLO-World) |
| Infrastructure | Run everything the same way on every machine | Docker Compose, GitHub Actions |

Common language: Python.

## Architecture principles

Every block is decoupled: it can be developed, run and tested alone.

- **Defined interfaces only.** Blocks talk through three contracts:
  - MCP tools between the agent and the twin, knowledge base and robot.
  - NGSI-LD entities for everything stored in the twin.
  - A robot command format between the robot MCP server and the robot controller.
- **Contracts first.** All three are written and agreed in M1. Any change goes through a PR reviewed by the owners of both sides.
- **One service per block.** Each block is its own Docker Compose service, startable without the others.
- **Mocks for neighbors.** Each contract comes with a mock, so a block can be tested without the real blocks around it.
- **Agent knows tools, not implementations.** Replacing a mock by the real block requires no change in the agent.

| Block | Tested alone with |
|-------|-------------------|
| Interface | Mock agent returning scripted answers |
| Agent | Mock MCP tools, scripted scenarios in French and English |
| Knowledge base | RAG test question set, scored automatically |
| Digital twin | Data model tests on Orion-LD: create, update, query, subscriptions |
| MCP servers | Tool calls against a test twin and test knowledge base |
| Vision | Labeled image set of the shelf: presence, identification, grasp state |
| Robot | Bench trials on fixed commands, without agent or twin |

On top of block tests, end-to-end tests run the reference scenarios on the full chain, from the walking skeleton (M3) onward.

## Technology choices

- **FIWARE as the single source of truth for "what is where"**: updated by every robot action and every inventory scan. Everything else reads from it.
- **Claude API first, local later**: reliable tool use from day one. Pydantic AI makes switching to a local model a configuration change.
- **Neo4j for hybrid RAG**: graph traversal for the BOM and vector search for documents in one database. Same hybrid RAG as a separate vector store, with less infrastructure.
- **ROS 2 for the robot**: official PIPER driver, teleoperation and recording. LeRobot handles training.
- **SmolVLA instead of OpenVLA**: fast enough for real time on embedded compute. Fine-tuned with LoRA, as in proposal 7, to fit on one consumer GPU. Fallback: ACT policy (LeRobot).
- **Agent normalizes robot instructions**: whatever the user's language, the agent sends the VLA a short English instruction from a fixed format ("pick the propeller from slot B2"). VLA models are trained mostly on English, and a fixed format makes the dataset consistent.
- **Vision separate from the VLA**: a VLA does not report failure. The detector tells us whether a part is there, in the gripper, or on the floor.

## Compute

- **Training**: one run on one GPU, at least 12 GB VRAM. Splitting one training across PCs over a home or school network is slower than a single GPU.
- **Team GPUs in parallel**: each member's GPU runs a different experiment (SmolVLA vs ACT, hyperparameters, dataset variants).
- **Inference**: target is an embedded NVIDIA Jetson next to the robot. Fallback: a laptop GPU.
- **Known hardware**: Florian's laptop, RTX 3050 Laptop (4 GB). Enough for detector inference and probably SmolVLA inference, too small for training.
- **Fallback**: school GPUs or rented cloud GPU.

## Compliance with proposals 7 and 10

| Requirement | How we meet it |
|-------------|----------------|
| P7 - PIPER master-slave teleoperation with synchronized RGB-D feedback | ROS 2 leader-follower teleoperation and recording, M1-M2 |
| P7 - Imitation dataset: trajectories, video, text instructions | Store and retrieve demonstrations, M4-M5 |
| P7 - VLA fine-tuning (OpenVLA or similar) via LoRA/Q-LoRA | SmolVLA fine-tuned with LoRA |
| P7 - Deployment on embedded compute (Jetson type) | Jetson target, laptop fallback |
| P7 - Real-time inference, robustness to lighting and target displacement | Robustness criteria below |
| P7 - Physical demo on voice or text command with success rate | Text command, voice as stretch goal; success criteria below |
| P7 - Construction finishing work (application domain) | **Changed**: warehouse handling. Same skills (VLA, imitation learning, ROS 2) |
| P10 - Hybrid RAG with graph and vector search | Neo4j graph + vector index |
| P10 - Orion Context Broker simulating inventory and sensors | Real inventory by vision + simulated sensors |
| P10 - MCP server for the agent to query FIWARE | Built by us |
| P10 - Chat or voice interface for technical and logistic queries | Text chat: procedure + part location + supply status in one answer |
| P10 - Real-time supply chain status | Simulated purchase orders and supplier lead times in the twin |
| P10 - Maintenance manuals and standards | Both indexed in the knowledge base |
| P10 - Multilingual documentation | English public docs + French procedures; questions and answers in both languages |
| P10 - Naval context | Underwater vehicle as reference product |

The application domain change must be approved by the supervisors.

## Team workstreams

| Member | Workstream |
|--------|------------|
| Florian (lead) | Digital twin (FIWARE data model), robot integration, overall integration |
| Adrien | Knowledge base, MCP servers for twin and knowledge base, infrastructure and CI |
| Antoine | Reference product dataset and shelf layout, safety and confirmation rules, test protocols and metrics |
| Louis-Marie | Agent, robot MCP server, VLA training |

## Milestones

| Period | Milestone | Done when |
|--------|-----------|-----------|
| M1-M2 | Foundations | Interface contracts and mocks agreed, product data sourced, shelf built, PIPER teleoperated under ROS 2, twin data model in Orion-LD, BOM in Neo4j |
| M3 | Walking skeleton | Chat to agent to twin + knowledge base + scripted robot move, end to end |
| M4-M5 | Data | Demonstrations recorded for each slot (including drops), detector tuned on our parts, RAG test question set |
| M6-M7 | Intelligence | SmolVLA trained, inventory scan updates the twin, confirmation flow in place |
| M8-M9 | Integration | All scenarios end to end, Jetson deployment, robustness tests, local LLM trial |
| M10 | Validation | Validation report, final defense |

## Success criteria

Targets to be confirmed after the first tests.

- Store and retrieve success rate of at least 80% over 20 trials each.
- Success rate maintained under lighting changes and with parts shifted in their slot.
- Twin matches the physical shelf after every task and every scan.
- Manual changes to the shelf detected at the next scan.
- Missing part always detected and reported, never a silent failure.
- Correct answers on at least 85% of the RAG test question set, in French and in English.
- Robot requests in French or English lead to the same robot action.
- 100% of physical actions confirmed by a human and traced in the twin.

## Main risks

| Risk | Mitigation |
|------|------------|
| Public data of the reference product incomplete | Check OpenROV files in M1; complete the BOM ourselves or switch to the fallback |
| Shelf slots hard to reach for the arm | Design the shelf around the PIPER workspace in M1, open-top bins |
| PIPER not supported by LeRobot out of the box | Check in M1; write a LeRobot adapter on top of the ROS 2 driver |
| Not enough VRAM for VLA training | Identify a 12 GB+ GPU in M1; school or cloud as fallback |
| VLA success rate too low | Fall back to ACT, or to scripted grasp guided by the detector |
| Late integration | Contracts in M1, walking skeleton at M3, end-to-end tests from then on |
| Blocks pass alone but fail together | Contracts reviewed by both sides, mocks kept in sync with real blocks |

## Open questions

- Supervisors' approval of the merge and the domain change.
- Is a Jetson provided with the PIPER? Which cameras?
- Is a leader arm available for master-slave teleoperation (second PIPER or equivalent)?
- GPU models and VRAM of Adrien, Antoine and Louis-Marie (run `nvidia-smi`).
- Which parts of the vehicle go on the shelf (count, size, how similar they look)?
