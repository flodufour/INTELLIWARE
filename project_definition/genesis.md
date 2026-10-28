# INTELLIWARE - Genesis

Founding document of the project: who we are, what we build, and why.

## Team

| Member | Apprenticeship | Domain |
|--------|----------------|--------|
| Florian Dufour (project lead) | Manitou | Industrial IT |
| Adrien | Thales | IT |
| Antoine | Thales | Quality |
| Louis-Marie | Devoteam | Agentic AI |

Project lead contact: florian.dufour@edu.devinci.fr

## Origin

The project merges two proposals from `project_propositions.pdf`:

- **Project 7 - VLA control of a PIPER robot**: a Vision-Language-Action model, fine-tuned by imitation learning, drives a robot arm from natural-language instructions.
- **Project 10 - FIWARE-Naval-RAG**: an AI agent combines a hybrid RAG (graph + vector) over technical documentation and BOM with real-time plant data from a FIWARE Context Broker, accessed through MCP.

Project 10 gives the agent the knowledge and the plant context. Project 7 lets it act in the physical world. Together they form a full loop: **understand, decide, act, trace**.

## Vision

An industrial AI agent that a technician queries by voice or text. The agent:

1. Retrieves the relevant procedure and parts from the documentation and BOM (hybrid RAG).
2. Checks the live state of the plant (stock, sensors, robot status) in FIWARE through MCP.
3. Delegates a physical task to a PIPER arm controlled by a VLA model.
4. Writes the result back to the FIWARE digital twin for traceability.

Example scenario: "Part X is faulty on line 2. What is the procedure, is a spare in stock, and can the robot bring it to the station?"

## Why it fits all our domains

- **Industrial IT (Manitou)**: shop-floor data, IoT, digital twin, NGSI-LD standards.
- **IT (Thales)**: software architecture, data infrastructure, deployment, security of an industrial system.
- **Quality (Thales)**: procedure compliance, traceability of every action, validation protocols, success-rate metrics.
- **Agentic AI (Devoteam)**: agent orchestration, MCP tools, RAG, VLA fine-tuning.

## Architecture

| Layer | Technology | Role |
|-------|------------|------|
| Knowledge (BOM) | Neo4j | Graph of assemblies, parts and relations |
| Documentation | Vector DB (Qdrant or Milvus) | Semantic search over manuals and procedures |
| Plant context | FIWARE Orion Context Broker (NGSI-LD) | Real-time digital twin: stock, sensors, robot state |
| Agent | LLM + MCP servers | Orchestrates RAG, FIWARE and robot tools |
| Action | PIPER arm, ROS 2, VLA model (e.g. OpenVLA) | Executes physical tasks from instructions |
| Compute | NVIDIA Jetson (or equivalent) | On-board VLA inference |
| Interface | Chat / voice | Technician entry point |

## Expected deliverables

- Hybrid RAG infrastructure (graph + vector) on a simulated industrial dataset.
- FIWARE Context Broker simulating inventory, sensors and robot state.
- MCP servers exposing FIWARE and the robot to the agent.
- Teleoperation setup and imitation dataset for the PIPER arm.
- Fine-tuned VLA model deployed on embedded compute.
- End-to-end demonstrator with a validation report (answer accuracy, task success rate, traceability).

## Proposed roles

To be confirmed by the team.

| Member | Main workstream |
|--------|-----------------|
| Florian | Project lead, FIWARE digital twin, system integration |
| Adrien | Data infrastructure (Neo4j, vector DB), backend, deployment |
| Antoine | Requirements, quality procedures dataset, test and validation protocols |
| Louis-Marie | Agent and MCP orchestration, RAG, VLA fine-tuning |

## Timeline

| Period | Phase | Key objectives |
|--------|-------|----------------|
| Months 1-2 | S1 - Setup | State of the art, architecture, Neo4j and vector DB, PIPER arm under ROS 2 |
| Months 3-5 | S1 - Foundations | Hybrid RAG pipeline, teleoperation and dataset collection |
| Months 6-7 | S2 - Context and learning | FIWARE Context Broker, MCP servers, VLA fine-tuning (LoRA) |
| Months 8-10 | S2 - Integration | Agent drives the robot end to end, robustness tests, final defense |

## Open questions

- Which physical task does the robot perform in the demo?
- Which industrial dataset do we simulate (BOM, manuals, stock)?
- Hardware availability: PIPER arm, RGB-D camera, Jetson.
- Which LLM: hosted API or local model?
