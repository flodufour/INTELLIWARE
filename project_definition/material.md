# INTELLIWARE - Material

Everything the project needs physically, who provides it and where we stand. Update the status as soon as something changes. Tracked in issue [#7](https://github.com/flodufour/INTELLIWARE/issues/7) (school hardware) and [#17](https://github.com/flodufour/INTELLIWARE/issues/17) (training GPU).

Status: **Have**, **To confirm** (asked, no answer yet), **Missing** (nobody has it yet).

## Robot and sensors

| Item | Purpose | Source | Status | Notes |
|------|---------|--------|--------|-------|
| PIPER arm (follower) | Stores and retrieves parts | School | To confirm | Availability date needed |
| Leader arm | Teleoperation to record demonstrations | School | To confirm | Second PIPER or dedicated leader arm. Fallback: SpaceMouse (about 150 EUR) |
| USB-CAN adapter | PIPER communication | School | To confirm | Normally shipped with the PIPER |
| Fixed RGB-D camera | Shelf scan, part identification | School | To confirm | E.g. Intel RealSense D435 |
| Wrist camera | View of the part during grasp | School or us | To confirm | USB webcam mounted on the gripper (20 to 50 EUR) |
| Jetson | Embedded inference | School | To confirm | Stretch goal only |

## Compute

| Item | Purpose | Source | Status | Notes |
|------|---------|--------|--------|-------|
| Inference laptop | ROS 2, vision and model next to the robot | Us | Have | Florian: RTX 3050 Laptop 4 GB, 16 GB RAM, driver 621.14, CUDA 13.5 |
| Services PC | Docker services: FIWARE, Neo4j, agent, chat | Us | Have | Florian's laptop for now; any 16 GB RAM PC |
| Training GPU, 12 GB+ VRAM | SmolVLA fine-tuning | Us, school or cloud | Missing | Issue #17. 16 to 24 GB preferred. Team GPUs: Adrien, Antoine, Louis-Marie to report (`nvidia-smi`) |

## Built by us

| Item | Purpose | Source | Status | Notes |
|------|---------|--------|--------|-------|
| Shelf | 2 levels, 4 to 6 open-top slots within PIPER reach (about 60 cm) | Us | Missing | Issue [#14](https://github.com/flodufour/INTELLIWARE/issues/14) |
| Input/output tray | Where parts are dropped off and handed over | Us | Missing | Built with the shelf |
| Spare parts | 3 to 4 OpenROV part types, 3D printed | Us | Missing | Issue [#13](https://github.com/flodufour/INTELLIWARE/issues/13) |
| 3D printer | Print the parts | School or fablab | To confirm | |
| Arm mount | Arm fixed on a stable table | Us | Missing | Required for repeatable demonstrations |
| Lamp | Controlled lighting for robustness tests | Us | Missing | |

## Space

| Item | Purpose | Source | Status | Notes |
|------|---------|--------|--------|-------|
| Dedicated room or corner | Setup left in place between sessions | School | To confirm | Critical: if shelf or cameras move, recorded demonstrations lose their value |
