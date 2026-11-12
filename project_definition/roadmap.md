# INTELLIWARE - Roadmap

From November 4, 2026 to the **March 1, 2027** deadline (team deadline, one to two weeks before the end-of-year exams). What we build is in [scope.md](scope.md); this document says when and how.

## Tracking

- Board: [INTELLIWARE project](https://github.com/users/flodufour/projects/4)
- Milestones (one per sprint): [milestones](https://github.com/flodufour/INTELLIWARE/milestones)
- Issues: [all issues](https://github.com/flodufour/INTELLIWARE/issues)

## Overview

| Sprint | Dates | Goal | Ends with |
|--------|-------|------|-----------|
| [0](https://github.com/flodufour/INTELLIWARE/milestone/1) | Nov 4 - Nov 16 | Kickoff | Scope approved, contracts agreed, hardware confirmed |
| [1](https://github.com/flodufour/INTELLIWARE/milestone/2) | Nov 17 - Nov 27 | Robot first | Robot pipeline checked on one slot, software blocks running alone |
| - | Nov 30 - Dec 18 | Exams | No project work |
| [2](https://github.com/flodufour/INTELLIWARE/milestone/3) | Dec 21 - Jan 1 | Software | Software walking skeleton on the robot mock, first training run |
| [3](https://github.com/flodufour/INTELLIWARE/milestone/4) | Jan 4 - Jan 15 | Walking skeleton and data | First end-to-end chain on the real robot, demonstration dataset, SmolVLA trained |
| [4](https://github.com/flodufour/INTELLIWARE/milestone/5) | Jan 18 - Jan 29 | Integration | All scenarios on the real robot, fallbacks ready |
| [5](https://github.com/flodufour/INTELLIWARE/milestone/6) | Feb 1 - Feb 12 | Robustness | **VLA go/no-go (Feb 5)**, test campaign done, **feature freeze** |
| [6](https://github.com/flodufour/INTELLIWARE/milestone/7) | Feb 15 - Feb 26 | Delivery | Report, demo video, rehearsed defense |
| - | Mar 1 | Deadline | Final delivery |

Availability: the robot is at school, reachable until Nov 27 and from Jan 4. No project work during the exams (Nov 30 - Dec 18). Holidays (Dec 21 - Jan 1): software only, remote.

## Critical path

The robot is the longest chain and sets the pace:

hardware confirmed -> teleoperation -> shelf built -> demonstrations recorded -> VLA trained -> VLA integrated -> robustness tests

Any delay on this chain delays the whole project. With no robot access from Nov 28 to Jan 3, sprint 1 checks the whole robot pipeline on one slot and records what lets work continue remotely (demonstrations, shelf images). Software blocks (twin, knowledge base, agent) have more slack and use mocks until the robot is ready.

## Sprints

### Sprint 0 - Kickoff (Nov 4 - Nov 16)

| Member | Tasks |
|--------|-------|
| Florian | Send genesis and scope to supervisors for approval. Get the PIPER and cameras; check leader arm and Jetson. Draft the NGSI-LD data model. Repository structure and Docker Compose skeleton |
| Adrien | CI pipeline. Neo4j running |
| Antoine | Source OpenROV data (BOM, manuals). Choose the 3 to 4 part types. Design the shelf within the PIPER workspace |
| Louis-Marie | Write the MCP tool contracts and the robot command format. Find a GPU with 12 GB+ VRAM |
| All | Agree on the contracts |

Tracked in issues [#6 to #17](https://github.com/flodufour/INTELLIWARE/milestone/1). The GitHub board, milestones and labels are set up.

### Sprint 1 - Robot first (Nov 17 - Nov 27)

Last two weeks with the robot before January: robot tasks come first.

| Member | Tasks |
|--------|-------|
| Florian | PIPER under ROS 2 with leader-follower teleoperation. Recording pipeline in LeRobot format. Scripted pick from one slot. Data model loaded in Orion-LD |
| Adrien | BOM ingested in Neo4j as a graph. Twin and knowledge base MCP servers started |
| Antoine | Provisional shelf and first printed parts. Images and videos of the shelf and parts for vision. Data formats of the BOM and procedures |
| Louis-Marie | Check that LeRobot drives the PIPER. Agent with mock tools (local Ollama until an API key is available). Streamlit chat |
| All | 10 to 20 demonstrations on one slot, uploaded to Hugging Face Hub |

Demo: robot teleoperated, demonstrations recorded, scripted pick from one slot; chat answers from mocks.

### Sprint 2 - Software (Dec 21 - Jan 1)

Holidays, remote, no robot.

| Member | Tasks |
|--------|-------|
| Florian | Simulator: sensors and alerts, stock thresholds, purchase orders, deliveries. Robot controller HTTP API (robot-command contract), arm calls stubbed |
| Adrien | Twin and knowledge base MCP servers on Orion-LD and Neo4j. Document ingestion and vector index |
| Antoine | Vision v1 on the recorded images: part presence per slot. French maintenance procedures. RAG test question set v1 (FR and EN). Safety and confirmation rules |
| Louis-Marie | Robot MCP server on the robot-command mock. Confirmation flow in the interface. Agent wired to the real twin and knowledge base. Short SmolVLA training on the November demonstrations, to validate the training pipeline |

Demo (Jan 4): **software walking skeleton**. A request in the chat goes through the real twin and knowledge base, runs a task on the robot mock and updates the twin.

### Sprint 3 - Walking skeleton and data (Jan 4 - Jan 15)

| Member | Tasks |
|--------|-------|
| Florian | Robot controller on the real arm: scripted move, then the model of sprint 2. Recording sessions and dataset quality checks |
| Adrien | Automated RAG evaluation in CI. Bilingual retrieval tuning. Live shelf view in the interface |
| Antoine | Final shelf built. Vision on the real shelf. Vision v2: grasp state (in gripper, dropped) |
| Louis-Marie | SmolVLA LoRA fine-tuning on the full dataset. Bench evaluation |
| All | First week: record demonstrations on every slot, store and retrieve, including drops and recoveries |

Demo: **first end-to-end chain on the real robot**. A request in the chat moves the robot and updates the twin. Trained gestures run on the bench.

### Sprint 4 - Integration (Jan 18 - Jan 29)

| Member | Tasks |
|--------|-------|
| Florian | VLA integrated in the robot controller. Store and retrieve end to end |
| Adrien | Replenish and Monitor end to end. Docker Compose on two machines |
| Antoine | Failure handling end to end: retry after drop, missing part reported. Inventory scan compared to the twin |
| Louis-Marie | SmolVLA retrained where it fails. ACT fallback trained. Agent handles all scenarios in French and English |
| All | Complete the dataset where the model fails |

Both fallbacks (ACT, scripted grasp guided by the detector) are ready by Jan 29.

### Sprint 5 - Robustness (Feb 1 - Feb 12)

**Go/no-go on Feb 5**: if the VLA success rate is far below 80%, switch to ACT or to scripted grasp guided by the detector. Either way, the VLA is evaluated and reported (proposal 7).

| Member | Tasks |
|--------|-------|
| Antoine | Test campaign: 20 trials per scenario, lighting changes, parts shifted in their slot |
| All | Fix what the tests reveal. Stretch goals only if all criteria are met (Jetson, voice) |

**Feature freeze on Feb 12**: no new features after this date, only fixes.

### Sprint 6 - Delivery (Feb 15 - Feb 26)

| Member | Tasks |
|--------|-------|
| Florian | Final report structure and integration of contributions |
| Antoine | Validation report with measured results |
| All | Demo video (backup if the live demo fails), slides, two full defense rehearsals |

## Way of working

We use a lightweight Scrum, adapted to four apprentices who are not available at the same time.

### Roles

| Role | Who | Responsibility |
|------|-----|----------------|
| Product owner | Florian | Owns the backlog, sets priorities, accepts finished work, single contact with supervisors |
| Scrum master | Antoine | Runs the meetings, removes blockers, enforces the definition of done |
| Developers | All four | Build, test, review |

### Rituals

| Ritual | When | Duration | Purpose |
|--------|------|----------|---------|
| Sprint planning | First day of the sprint | 1 h | Pick backlog items, split into tasks, assign |
| Async stand-up | Every working day | 2 min each | Message in the team channel: done, next, blocked |
| Weekly sync | Mid-sprint | 30 min | Resolve blockers, check integration |
| Sprint review | Last day of the sprint | 30 min | Live demo of what works, supervisors invited |
| Retrospective | Right after the review | 30 min | One thing to keep, one to change |

### Backlog

- Everything lives in GitHub: **one issue per task**, **one milestone per sprint**, a **[project board](https://github.com/users/flodufour/projects/4)** with columns Backlog, To do, In progress, Review, Done.
- Each issue states its owner, links to its sprint and to the relevant section of `scope.md`, and has a "Done when" criterion.
- Issues of later sprints are created at each sprint planning, from this roadmap.
- Issues are labeled by block: `agent`, `interface`, `twin`, `simulator`, `knowledge-base`, `mcp`, `vision`, `robot`, `infra`, `docs`.
- A task fits in at most 2 days of work. Larger ones are split.
- Issues are written as user stories when they bring visible value: "As a technician, I want to ask where a part is, so that I find it without searching."

### Definition of done

A task is done when:

- The code is merged to `main` through an approved PR ([CONTRIBUTING.md](../CONTRIBUTING.md)).
- Its tests pass in CI.
- It works with the real neighbors or with up-to-date mocks.
- Documentation is updated if behavior changed.
- It can be shown in the sprint review.

### Rules

- Every sprint ends with something that runs and can be shown.
- A blocker raised in the stand-up gets help the same day.
- Scope changes go through the product owner and are written in `scope.md`.
