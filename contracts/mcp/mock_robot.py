# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=2.3,<3"]
# ///
"""Mock robot MCP server (README.md). Simulated tasks, no controller.

Run: uv run mock_robot.py
"""

import asyncio
import os
import re
import uuid

from mcp.server.mcpserver import MCPServer

from models import SLOT_PATTERN, RobotStatus, Scan, Stopped, TaskResult, TrayPart, fail

TASK_SECONDS = 2
SHELF = {"A1": "propeller", "A2": "propeller", "A3": "cap", "B1": "clip", "B2": None, "B3": None}
state = {"task_id": None, "stop": False}

server = MCPServer("robot", instructions="PIPER arm and shelf vision. Physical actions need a human confirmation.")


def busy():
    return fail("robot_busy", f"task {state['task_id']} is running")


async def run_task(part: str, slot: str, confirmed_by: str, source: str, target: str) -> TaskResult:
    if not confirmed_by.strip():
        return fail("not_confirmed", "ask the technician to confirm, then pass their name as confirmed_by")
    if not re.match(SLOT_PATTERN, slot):
        return fail("invalid_argument", f"slot must match {SLOT_PATTERN}")
    if state["task_id"]:
        return busy()
    task_id = str(uuid.uuid4())
    state.update(task_id=task_id, stop=False)
    try:
        if slot == "Z9":
            return TaskResult(task_id=task_id, status="failed", failure="part_missing", attempts=0,
                              part_location="unknown", message=f"no part in {source}")
        attempts = 3 if part == "broken" else 1
        for attempt in range(1, attempts + 1):
            await asyncio.sleep(TASK_SECONDS / attempts)
            if state["stop"]:
                return TaskResult(task_id=task_id, status="stopped", failure=None, attempts=attempt,
                                  part_location="unknown", message="stopped on request")
        if part == "broken":
            return TaskResult(task_id=task_id, status="failed", failure="grasp_failed", attempts=attempts,
                              part_location=source, message="part dropped 3 times")
        return TaskResult(task_id=task_id, status="succeeded", failure=None, attempts=attempts,
                          part_location=target, message="done")
    finally:
        state["task_id"] = None


@server.tool()
def identify_tray_part() -> TrayPart:
    """Identify the part on the input/output tray with vision."""
    return TrayPart(part="propeller", confidence=0.93)


@server.tool()
async def store_part(part: str, slot: str, confirmed_by: str) -> TaskResult:
    """Move the part from the tray to the slot. Ask the technician to confirm first."""
    return await run_task(part, slot, confirmed_by, source="tray", target="slot")


@server.tool()
async def retrieve_part(part: str, slot: str, confirmed_by: str) -> TaskResult:
    """Bring the part from the slot to the tray. Ask the technician to confirm first."""
    return await run_task(part, slot, confirmed_by, source="slot", target="tray")


@server.tool()
def scan_shelf() -> Scan:
    """Scan the shelf with the fixed camera, correct the twin and report mismatches."""
    if state["task_id"]:
        return busy()
    seen = {**SHELF, "B1": None}
    return Scan.model_validate({
        "slots": [{"slot": s, "part": p} for s, p in seen.items()],
        "mismatches": [{"slot": s, "twin": SHELF[s], "seen": p} for s, p in seen.items() if SHELF[s] != p],
    })


@server.tool()
def stop_robot() -> Stopped:
    """Stop the arm at once."""
    state["stop"] = True
    return Stopped(stopped_task_id=state["task_id"])


@server.tool()
def get_robot_status() -> RobotStatus:
    """Whether the robot is idle or running a task."""
    return RobotStatus(state="busy" if state["task_id"] else "idle", task_id=state["task_id"])


if __name__ == "__main__":
    server.run("streamable-http", host=os.environ.get("HOST", "127.0.0.1"),
               port=int(os.environ.get("PORT", 8003)))
