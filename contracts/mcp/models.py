"""Output models and error helper of the MCP tool contracts (README.md).

Shared by the mocks and the real servers: a tool annotated with one of these
models publishes its JSON output schema to the agent.
"""

import json
from typing import Any, Literal

from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel

SLOT_PATTERN = r"^[A-Z][1-9]$"


def fail(code: str, message: str) -> Any:
    """Error result: isError true, text {"error": code, "message": message}.

    Return it from a tool instead of raising: a raised error gets an
    "Error executing tool" prefix and is no longer plain JSON.
    """
    text = json.dumps({"error": code, "message": message})
    return CallToolResult(content=[TextContent(type="text", text=text)], is_error=True)


class Names(BaseModel):
    en: str
    fr: str


# Twin

class Part(BaseModel):
    part: str
    names: Names
    stock: int
    threshold: int
    slots: list[str]


class Parts(BaseModel):
    parts: list[Part]


class Slot(BaseModel):
    slot: str
    level: int
    part: str | None


class Tray(BaseModel):
    part: str | None


class Shelf(BaseModel):
    slots: list[Slot]
    tray: Tray


class FreeSlot(BaseModel):
    slot: str


class PurchaseOrder(BaseModel):
    id: str
    part: str
    quantity: int
    supplier: str
    status: Literal["ordered", "delivered"]
    ordered_at: str
    expected_at: str


class PurchaseOrders(BaseModel):
    orders: list[PurchaseOrder]


class Sensor(BaseModel):
    sensor: str
    kind: Literal["temperature", "humidity"]
    value: float
    unit: str
    min: float | None
    max: float | None
    status: Literal["ok", "alert"]
    observed_at: str


class Sensors(BaseModel):
    sensors: list[Sensor]


class Alert(BaseModel):
    id: str
    sensor: str
    kind: Literal["temperature", "humidity"]
    value: float
    limit: float
    raised_at: str
    acknowledged_by: str | None
    acknowledged_at: str | None


class Alerts(BaseModel):
    alerts: list[Alert]


class Task(BaseModel):
    task_id: str
    action: Literal["store", "retrieve", "home"]
    part: str | None
    slot: str | None
    status: Literal["queued", "running", "succeeded", "failed", "stopped"]
    failure: str | None
    confirmed_by: str
    started_at: str | None
    finished_at: str | None


class Tasks(BaseModel):
    tasks: list[Task]


# Knowledge base

class Chunk(BaseModel):
    chunk_id: str
    text: str
    document: str
    section: str
    kind: Literal["manual", "procedure", "standard"]
    language: Literal["en", "fr"]
    procedure_id: str | None
    score: float


class Chunks(BaseModel):
    chunks: list[Chunk]


class Procedure(BaseModel):
    procedure_id: str
    title: str
    language: Literal["en", "fr"]
    steps: list[str]
    parts: list[str]
    document: str


class DocumentRef(BaseModel):
    document: str
    section: str


class Storage(BaseModel):
    temperature_min: float
    temperature_max: float
    humidity_max: float


class PartInfo(BaseModel):
    part: str
    names: Names
    assembly: str | None
    subparts: list[str]
    related_parts: list[str]
    documents: list[DocumentRef]
    procedures: list[str]
    storage: Storage


# Robot

class TrayPart(BaseModel):
    part: str | None
    confidence: float


class TaskResult(BaseModel):
    task_id: str
    status: Literal["succeeded", "failed", "stopped"]
    failure: Literal["part_missing", "target_occupied", "grasp_failed", "timeout", "robot_error"] | None
    attempts: int
    part_location: Literal["slot", "tray", "gripper", "unknown"] | None
    message: str


class SeenSlot(BaseModel):
    slot: str
    part: str | None


class Mismatch(BaseModel):
    slot: str
    twin: str | None
    seen: str | None


class Scan(BaseModel):
    slots: list[SeenSlot]
    mismatches: list[Mismatch]


class Stopped(BaseModel):
    stopped_task_id: str | None


class RobotStatus(BaseModel):
    state: Literal["idle", "busy", "error"]
    task_id: str | None
