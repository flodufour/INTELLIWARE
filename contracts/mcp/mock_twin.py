# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=2.3,<3"]
# ///
"""Mock twin MCP server (README.md). In-memory data. Run: uv run mock_twin.py"""

import os
from datetime import datetime, timezone
from typing import Literal

from mcp.server.mcpserver import MCPServer

from models import Alert, Alerts, FreeSlot, Part, Parts, PurchaseOrders, Sensors, Shelf, Tasks, fail

NAMES = {
    "propeller": {"en": "propeller", "fr": "hélice"},
    "cap": {"en": "battery tube cap", "fr": "bouchon de tube batterie"},
    "clip": {"en": "cable clip", "fr": "clip de câble"},
}
THRESHOLDS = {"propeller": 2, "cap": 1, "clip": 2}
SLOTS = {"A1": "propeller", "A2": "propeller", "A3": "cap", "B1": "clip", "B2": None, "B3": None}
TRAY = {"part": None}
ORDERS = [
    {"id": "PO-001", "part": "clip", "quantity": 4, "supplier": "OpenROV Store", "status": "ordered",
     "ordered_at": "2026-11-10T09:00:00Z", "expected_at": "2026-11-17T09:00:00Z"},
]
SENSORS = [
    {"sensor": "shelf-temperature", "kind": "temperature", "value": 19.5, "unit": "°C",
     "min": 10.0, "max": 30.0, "status": "ok", "observed_at": "2026-11-12T14:00:00Z"},
    {"sensor": "shelf-humidity", "kind": "humidity", "value": 72.0, "unit": "%",
     "min": None, "max": 60.0, "status": "alert", "observed_at": "2026-11-12T14:00:00Z"},
]
ALERTS = [
    {"id": "AL-001", "sensor": "shelf-humidity", "kind": "humidity", "value": 72.0, "limit": 60.0,
     "raised_at": "2026-11-12T13:55:00Z", "acknowledged_by": None, "acknowledged_at": None},
]
TASKS = [
    {"task_id": "3f2b8c1e-9a4d-4e7b-8f0a-2c6d1e5b7a90", "action": "store", "part": "cap", "slot": "A3",
     "status": "succeeded", "failure": None, "confirmed_by": "Antoine",
     "started_at": "2026-11-12T10:00:00Z", "finished_at": "2026-11-12T10:00:40Z"},
]

server = MCPServer("twin", instructions="Live state of the INTELLIWARE shelf.")


def unknown_part(part: str):
    return fail("not_found", f"unknown part '{part}'")


def part_view(part: str) -> Part:
    slots = [s for s, p in SLOTS.items() if p == part]
    return Part.model_validate({"part": part, "names": NAMES[part], "stock": len(slots),
            "threshold": THRESHOLDS[part], "slots": slots})


@server.tool()
def list_parts() -> Parts:
    """List every part type with its stock and slots."""
    return Parts(parts=[part_view(p) for p in NAMES])


@server.tool()
def get_part(part: str) -> Part:
    """Stock, threshold and slots of one part type."""
    if part not in NAMES:
        return unknown_part(part)
    return part_view(part)


@server.tool()
def get_shelf() -> Shelf:
    """Content of every slot and of the tray."""
    slots = [{"slot": s, "level": ord(s[0]) - ord("A") + 1, "part": p} for s, p in SLOTS.items()]
    return Shelf.model_validate({"slots": slots, "tray": TRAY})


@server.tool()
def find_free_slot(part: str) -> FreeSlot:
    """Free slot where a part of this type should be stored."""
    if part not in NAMES:
        return unknown_part(part)
    for slot, content in SLOTS.items():
        if content is None:
            return FreeSlot(slot=slot)
    return fail("shelf_full", "no free slot")


@server.tool()
def list_purchase_orders(part: str | None = None,
                         status: Literal["ordered", "delivered"] | None = None) -> PurchaseOrders:
    """Purchase orders, optionally filtered by part and status."""
    if part is not None and part not in NAMES:
        return unknown_part(part)
    return PurchaseOrders.model_validate({"orders": [
        o for o in ORDERS if (part is None or o["part"] == part) and (status is None or o["status"] == status)]})


@server.tool()
def list_sensors() -> Sensors:
    """Latest value of every simulated sensor."""
    return Sensors.model_validate({"sensors": SENSORS})


@server.tool()
def list_alerts(active_only: bool = True) -> Alerts:
    """Sensor alerts; active means not acknowledged."""
    return Alerts.model_validate({"alerts": [a for a in ALERTS if not active_only or a["acknowledged_by"] is None]})


@server.tool()
def acknowledge_alert(alert_id: str, by: str) -> Alert:
    """Record that the technician was informed of an alert."""
    for alert in ALERTS:
        if alert["id"] == alert_id:
            alert["acknowledged_by"] = by
            alert["acknowledged_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            return Alert.model_validate(alert)
    return fail("not_found", f"unknown alert '{alert_id}'")


@server.tool()
def list_tasks(limit: int = 10) -> Tasks:
    """Latest robot tasks, newest first."""
    return Tasks.model_validate({"tasks": TASKS[::-1][:limit]})


if __name__ == "__main__":
    server.run("streamable-http", host=os.environ.get("HOST", "127.0.0.1"),
               port=int(os.environ.get("PORT", 8001)))
