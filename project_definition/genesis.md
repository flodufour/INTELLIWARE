# INTELLIWARE - Genesis

Who we are and why this project. What we build is in [scope.md](scope.md), when in [roadmap.md](roadmap.md).

## Team

| Member | Apprenticeship | Domain |
|--------|----------------|--------|
| Florian Dufour (project lead) | Manitou | Industrial IT |
| Adrien | Thales | IT |
| Antoine | Thales | Quality |
| Louis-Marie | Devoteam | Agentic AI |

Project lead contact: florian.dufour@edu.devinci.fr

## Origin

The project merges two proposals from [project_propositions.pdf](project_propositions.pdf):

- **Project 7 - VLA control of a PIPER robot**: a Vision-Language-Action model, fine-tuned by imitation learning, drives a robot arm from natural-language instructions.
- **Project 10 - FIWARE-Naval-RAG**: an AI agent combines a hybrid RAG (graph + vector) over technical documentation and BOM with live plant data from a FIWARE Context Broker, accessed through MCP.

Project 10 gives the agent knowledge and context. Project 7 lets it act. Together: **understand, decide, act, trace**.

## Vision

A technician talks to a smart warehouse. The agent finds the procedure and the part in the documentation, checks the live stock in the digital twin, has the robot fetch the part, and records the action in the twin.

Example: "The thruster propeller is broken. What is the procedure, do we have a spare, and can the robot bring it?"

## Why it fits our domains

- **Industrial IT (Manitou)**: digital twin, NGSI-LD, shop-floor data.
- **IT (Thales)**: architecture, data infrastructure, deployment.
- **Quality (Thales)**: traceability, validation protocols, success metrics.
- **Agentic AI (Devoteam)**: agent, MCP tools, RAG, VLA fine-tuning.
