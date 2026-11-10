# INTELLIWARE - Roadmap

From November 4, 2026 to the **March 1, 2027** deadline (team deadline, one to two weeks before the end-of-year exams). What we build is in [scope.md](scope.md); this document says when and how.

## Tracking

- Board: [INTELLIWARE project](https://github.com/users/flodufour/projects/4)
- Milestones (one per sprint): [milestones](https://github.com/flodufour/INTELLIWARE/milestones)
- Issues: [all issues](https://github.com/flodufour/INTELLIWARE/issues)

## Overview

| Sprint | Dates | Goal | Ends with |
|--------|-------|------|-----------|
| [0](https://github.com/flodufour/INTELLIWARE/milestone/1) | Nov 4 - Nov 13 | Kickoff | Scope approved, contracts agreed, hardware confirmed |
| [1](https://github.com/flodufour/INTELLIWARE/milestone/2) | Nov 16 - Nov 27 | Foundations | Every block runs alone, robot teleoperated |
| [2](https://github.com/flodufour/INTELLIWARE/milestone/3) | Nov 30 - Dec 11 | Walking skeleton | First end-to-end chain |
| [3](https://github.com/flodufour/INTELLIWARE/milestone/4) | Dec 14 - Dec 18 | Data collection | Demonstration dataset started, training pipeline tested |
| - | Dec 21 - Jan 1 | Holidays | Buffer, long training runs can run unattended |
| [4](https://github.com/flodufour/INTELLIWARE/milestone/5) | Jan 4 - Jan 15 | Intelligence | SmolVLA trained, vision complete, supply chain simulated |
| [5](https://github.com/flodufour/INTELLIWARE/milestone/6) | Jan 18 - Jan 29 | Integration | All scenarios end to end, **VLA go/no-go** |
| [6](https://github.com/flodufour/INTELLIWARE/milestone/7) | Feb 1 - Feb 12 | Robustness | Test campaign done, **feature freeze** |
| [7](https://github.com/flodufour/INTELLIWARE/milestone/8) | Feb 15 - Feb 26 | Delivery | Report, demo video, rehearsed defense |
| - | Mar 1 | Deadline | Final delivery |

## Critical path

The robot is the longest chain and sets the pace:

hardware confirmed -> teleoperation -> shelf built -> demonstrations recorded -> VLA trained -> VLA integrated -> robustness tests

Any delay on this chain delays the whole project. Software blocks (twin, knowledge base, agent) have more slack and use mocks until the robot is ready.

## Sprints

### Sprint 0 - Kickoff (Nov 4 - Nov 13)

| Member | Tasks |
|--------|-------|
| Florian | Send genesis and scope to supervisors for approval. Get the PIPER and cameras; check leader arm and Jetson. Draft the NGSI-LD data model. Repository structure and Docker Compose skeleton |
| Adrien | CI pipeline. Neo4j running |
| Antoine | Source OpenROV data (BOM, manuals). Choose the 3 to 4 part types. Design the shelf within the PIPER workspace |
| Louis-Marie | Write the MCP tool contracts and the robot command format. Find a GPU with 12 GB+ VRAM |
| All | Agree on the contracts |

Tracked in issues [#6 to #17](https://github.com/flodufour/INTELLIWARE/milestone/1). The GitHub board, milestones and labels are set up.

### Sprint 1 - Foundations (Nov 16 - Nov 27)

| Member | Tasks |
|--------|-------|
| Florian | Orion-LD and MongoDB running, data model loaded. PIPER under ROS 2 with leader-follower teleoperation |
| Adrien | BOM ingested in Neo4j as a graph. Document ingestion pipeline started |
| Antoine | Shelf built, parts printed. First French maintenance procedures. RAG test question set v1 (FR and EN) |
| Louis-Marie | Agent on Claude API with mock tools. Streamlit chat |

Demo: chat answers from mocks; robot moved by teleoperation.

### Sprint 2 - Walking skeleton (Nov 30 - Dec 11)

| Member | Tasks |
|--------|-------|
| Florian | Simulator v1 (sensors). Scripted pick from one slot |
| Adrien | Twin and knowledge base MCP servers. Vector index on documents |
| Antoine | Vision v1: part presence per slot. Safety and confirmation rules written |
| Louis-Marie | Robot MCP server on the scripted move. Confirmation flow. Agent wired to the real twin and knowledge base |

Demo: **first end-to-end chain**. A request in the chat moves the robot and updates the twin.

### Sprint 3 - Data collection (Dec 14 - Dec 18)

| Member | Tasks |
|--------|-------|
| Florian | Recording pipeline in LeRobot format |
| Louis-Marie | First SmolVLA training run on a small dataset, to validate the pipeline |
| All | Record demonstrations: every slot, store and retrieve, including drops and recoveries |

Holidays (Dec 21 - Jan 1): no planned work. Long training runs can run unattended.

### Sprint 4 - Intelligence (Jan 4 - Jan 15)

| Member | Tasks |
|--------|-------|
| Florian | Simulator v2: stock thresholds, purchase orders, deliveries, sensor alerts. Twin updated by robot actions |
| Adrien | Automated RAG evaluation in CI. Bilingual retrieval tuning. Live shelf view in the interface |
| Antoine | Vision v2: grasp state (in gripper, dropped). Inventory scan compared to the twin |
| Louis-Marie | SmolVLA LoRA fine-tuning on the full dataset. Bench evaluation |
| All | Complete the dataset where the model fails |

Demo: robot executes trained gestures on the bench; inventory scan detects a moved part.

### Sprint 5 - Integration (Jan 18 - Jan 29)

| Member | Tasks |
|--------|-------|
| Florian | VLA integrated in the robot controller. Store and retrieve end to end |
| Adrien | Replenish scenario end to end. Docker Compose split per machine |
| Antoine | Failure handling end to end: retry after drop, missing part reported |
| Louis-Marie | Agent handles all scenarios in French and English |

**Go/no-go on Jan 29**: if the VLA success rate is far below 80%, switch to ACT or to scripted grasp guided by the detector. Both fallbacks must be ready by then.

### Sprint 6 - Robustness (Feb 1 - Feb 12)

| Member | Tasks |
|--------|-------|
| Antoine | Test campaign: 20 trials per scenario, lighting changes, parts shifted in their slot |
| All | Fix what the tests reveal. Stretch goals only if all criteria are met (Jetson, voice, local LLM) |

**Feature freeze on Feb 12**: no new features after this date, only fixes.

### Sprint 7 - Delivery (Feb 15 - Feb 26)

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
| Sprint planning | First Monday of the sprint | 1 h | Pick backlog items, split into tasks, assign |
| Async stand-up | Every working day | 2 min each | Message in the team channel: done, next, blocked |
| Weekly sync | Mid-sprint | 30 min | Resolve blockers, check integration |
| Sprint review | Last Friday of the sprint | 30 min | Live demo of what works, supervisors invited |
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
