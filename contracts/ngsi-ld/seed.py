"""Load the starting state of the twin into Orion-LD (README.md).

Same data as the MCP mocks (contracts/mcp). Standard library only.
Run: python seed.py   (Orion-LD at ORION_URL, default http://localhost:1026)
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ORION = os.environ.get("ORION_URL", "http://localhost:1026") + "/ngsi-ld/v1"
TYPES = ["Shelf", "Slot", "Tray", "PartType", "Supplier", "PurchaseOrder",
         "Sensor", "Alert", "Robot", "Task"]


def urn(kind: str, key: str) -> str:
    return f"urn:ngsi-ld:{kind}:{key}"


def prop(value, **extra) -> dict:
    return {"type": "Property", "value": value, **extra}


def rel(kind: str, key: str) -> dict:
    return {"type": "Relationship", "object": urn(kind, key)}


def entity(kind: str, key: str, **attrs) -> dict:
    return {"id": urn(kind, key), "type": kind, **attrs}


SHELF = "1"
SUPPLIER = "openrov-store"
PARTS = {  # key: (en, fr, BOM reference placeholder until #12/#13, threshold)
    "propeller": ("propeller", "hélice", "OROV-THR-PROP-01", 2),
    "cap": ("battery tube cap", "bouchon de tube batterie", "OROV-BAT-CAP-01", 1),
    "clip": ("cable clip", "clip de câble", "OROV-TET-CLIP-01", 2),
}
SLOTS = {"A1": "propeller", "A2": "propeller", "A3": "cap",
         "B1": "clip", "B2": None, "B3": None}


def slot(key: str, part: str | None) -> dict:
    attrs = {"level": prop(ord(key[0]) - ord("A") + 1), "position": prop(int(key[1])),
             "refShelf": rel("Shelf", SHELF)}
    if part:
        attrs["refPartType"] = rel("PartType", part)
    return entity("Slot", key, **attrs)


ENTITIES = [
    entity("Shelf", SHELF, name=prop("Spare parts shelf"), levels=prop(2)),
    entity("Tray", "1", refShelf=rel("Shelf", SHELF)),
    entity("Supplier", SUPPLIER, name=prop("OpenROV Store"), leadTimeDays=prop(7)),
    *[entity("PartType", key, name=prop({"en": en, "fr": fr}), bomRef=prop(bom),
             stockThreshold=prop(threshold), reorderQuantity=prop(4),
             refSupplier=rel("Supplier", SUPPLIER))
      for key, (en, fr, bom, threshold) in PARTS.items()],
    *[slot(key, part) for key, part in SLOTS.items()],
    entity("PurchaseOrder", "PO-001", refPartType=rel("PartType", "clip"),
           refSupplier=rel("Supplier", SUPPLIER), quantity=prop(4), status=prop("ordered"),
           orderedAt=prop("2026-11-10T09:00:00Z"), expectedAt=prop("2026-11-17T09:00:00Z")),
    entity("Sensor", "shelf-temperature", controlledProperty=prop("temperature"),
           value=prop(19.5, unitCode="CEL", observedAt="2026-11-12T14:00:00Z"),
           minValue=prop(10.0), maxValue=prop(30.0), status=prop("ok"),
           refShelf=rel("Shelf", SHELF)),
    entity("Sensor", "shelf-humidity", controlledProperty=prop("humidity"),
           value=prop(72.0, unitCode="P1", observedAt="2026-11-12T14:00:00Z"),
           maxValue=prop(60.0), status=prop("alert"), refShelf=rel("Shelf", SHELF)),
    entity("Alert", "AL-001", category=prop("environment"), subCategory=prop("humidity"),
           refSensor=rel("Sensor", "shelf-humidity"), value=prop(72.0), threshold=prop(60.0),
           dateIssued=prop("2026-11-12T13:55:00Z")),
    entity("Robot", "piper-1", state=prop("idle")),
    entity("Task", "3f2b8c1e-9a4d-4e7b-8f0a-2c6d1e5b7a90", action=prop("store"),
           refPartType=rel("PartType", "cap"), refSlot=rel("Slot", "A3"),
           status=prop("succeeded"), attempts=prop(1), partLocation=prop("slot"),
           confirmedBy=prop("Antoine"), startedAt=prop("2026-11-12T10:00:00Z"),
           finishedAt=prop("2026-11-12T10:00:40Z")),
]


def request(method: str, path: str, body=None):
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(ORION + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            text = res.read()
    except urllib.error.HTTPError as err:
        sys.exit(f"{method} {path}: {err.code} {err.read().decode()}")
    except urllib.error.URLError as err:
        sys.exit(f"Orion-LD not reachable at {ORION}: {err.reason}")
    return json.loads(text) if text else None


def query(kind: str, q: str | None = None) -> list[dict]:
    params = {"type": kind, "limit": 1000, "options": "keyValues"}
    if q:
        params["q"] = q
    return request("GET", "/entities?" + urllib.parse.urlencode(params))


def key(entity_id: str) -> str:
    return entity_id.rsplit(":", 1)[1]


def main() -> None:
    old = [e["id"] for kind in TYPES for e in query(kind)]
    if old:
        request("POST", "/entityOperations/delete", old)
    request("POST", "/entityOperations/create", ENTITIES)
    print(f"Deleted {len(old)} entities, created {len(ENTITIES)}.")

    for part in PARTS:
        slots = sorted(key(s["id"]) for s in query("Slot", f'refPartType=="{urn("PartType", part)}"'))
        print(f"  {part}: stock {len(slots)} {slots}")
    print("  free slots:", sorted(key(s["id"]) for s in query("Slot", "!refPartType")))
    print("  active alerts:", [key(a["id"]) for a in query("Alert", "!acknowledgedBy")])


if __name__ == "__main__":
    main()
