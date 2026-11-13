# ngsi-ld

NGSI-LD data model of the digital twin (Orion-LD). Issue #8.

The twin holds the live state of the shelf. Every block that reads or writes it uses the entities below, and nothing else. The [MCP tools](../mcp/) of the twin server are built on this model.

[seed.py](seed.py) loads a starting state, the same as the [MCP mocks](../mcp/): the real twin server can then be compared with its mock.

## Conventions

- **Ids**: `urn:ngsi-ld:<Type>:<key>`. The key is the id used everywhere else: `urn:ngsi-ld:PartType:propeller` is part `propeller`, `urn:ngsi-ld:Slot:B2` is slot `B2` (see [MCP conventions](../mcp/#conventions)).
- **Attribute names**: camelCase. Relationships start with `ref` and point to an entity id (`refPartType`, `refSlot`).
- **Context**: NGSI-LD core context only. Send `Content-Type: application/json` with no `Link` header; short names are expanded the same way for every block.
- **No null**: an attribute with no value is absent. Set an attribute with `POST /entities/{id}/attrs` (creates or overwrites it), clear it with `DELETE /entities/{id}/attrs/{attr}`. Merge-patch with `urn:ngsi-ld:null` is not available in Orion-LD 1.6.
- **Times**: ISO 8601 UTC strings (`2026-11-12T14:00:00Z`). Sensor readings use the NGSI-LD `observedAt` and `unitCode` (UN/CEFACT: `CEL` for degrees Celsius, `P1` for percent).
- **Numbers**: Orion-LD returns `72.0` as `72` and adds milliseconds to `observedAt`; readers cast and format.
- **Text**: send UTF-8 as is (`json.dumps(..., ensure_ascii=False)`). Orion-LD 1.6 keeps `é` escapes literally inside object values. `LanguageProperty` is not supported, so names in two languages are an object `{"en": ..., "fr": ...}`.
- **Stock is not stored**: a slot holds one part, so the stock of a part type is the number of slots whose `refPartType` points to it. One source of truth, nothing to keep in sync.
- **No Part entity**: parts of one type are identical and not tracked one by one. A slot points to its part type.

## Entities

| Entity | Id example | Written by |
|--------|------------|------------|
| Shelf | `urn:ngsi-ld:Shelf:1` | seed |
| Slot | `urn:ngsi-ld:Slot:B2` | seed; `refPartType` by the robot server |
| Tray | `urn:ngsi-ld:Tray:1` | seed; `refPartType` by the robot server |
| PartType | `urn:ngsi-ld:PartType:propeller` | seed |
| Supplier | `urn:ngsi-ld:Supplier:openrov-store` | seed |
| PurchaseOrder | `urn:ngsi-ld:PurchaseOrder:PO-001` | simulator |
| Sensor | `urn:ngsi-ld:Sensor:shelf-humidity` | seed; readings by the simulator |
| Alert | `urn:ngsi-ld:Alert:AL-001` | simulator; acknowledgement by the twin server |
| Robot | `urn:ngsi-ld:Robot:piper-1` | robot server |
| Task | `urn:ngsi-ld:Task:<task_id>` | robot server |

"Seed" is the setup data, loaded once by [seed.py](seed.py) and changed only when the physical shelf changes.

### Shelf

| Attribute | Type | Value |
|-----------|------|-------|
| `name` | Property | Text |
| `levels` | Property | Integer, `2` |

### Slot

| Attribute | Type | Value |
|-----------|------|-------|
| `level` | Property | Integer, `1` for `A`, `2` for `B` |
| `position` | Property | Integer, `1` to `9` |
| `refShelf` | Relationship | Shelf |
| `refPartType` | Relationship | PartType of the part in the slot. Absent when the slot is free |

```json
{
  "id": "urn:ngsi-ld:Slot:A1",
  "type": "Slot",
  "level": {"type": "Property", "value": 1},
  "position": {"type": "Property", "value": 1},
  "refShelf": {"type": "Relationship", "object": "urn:ngsi-ld:Shelf:1"},
  "refPartType": {"type": "Relationship", "object": "urn:ngsi-ld:PartType:propeller"}
}
```

### Tray

The input/output tray. Same `refShelf` and `refPartType` as a slot, no `level` or `position`.

### PartType

| Attribute | Type | Value |
|-----------|------|-------|
| `name` | Property | `{"en": "propeller", "fr": "hélice"}` |
| `bomRef` | Property | Reference in the OpenROV BOM, shared with the knowledge base (e.g. `OROV-THR-PROP-01`, final values from #12 and #13) |
| `stockThreshold` | Property | Integer. Below it, the simulator orders |
| `reorderQuantity` | Property | Integer, quantity of a purchase order |
| `refSupplier` | Relationship | Supplier |

```json
{
  "id": "urn:ngsi-ld:PartType:propeller",
  "type": "PartType",
  "name": {"type": "Property", "value": {"en": "propeller", "fr": "hélice"}},
  "bomRef": {"type": "Property", "value": "OROV-THR-PROP-01"},
  "stockThreshold": {"type": "Property", "value": 2},
  "reorderQuantity": {"type": "Property", "value": 4},
  "refSupplier": {"type": "Relationship", "object": "urn:ngsi-ld:Supplier:openrov-store"}
}
```

### Supplier

| Attribute | Type | Value |
|-----------|------|-------|
| `name` | Property | Text |
| `leadTimeDays` | Property | Integer, delivery time used by the simulator |

### PurchaseOrder

| Attribute | Type | Value |
|-----------|------|-------|
| `refPartType` | Relationship | PartType |
| `refSupplier` | Relationship | Supplier |
| `quantity` | Property | Integer |
| `status` | Property | `ordered` or `delivered` |
| `orderedAt` | Property | Time |
| `expectedAt` | Property | Time |
| `deliveredAt` | Property | Time. Absent until delivered |

### Sensor

| Attribute | Type | Value |
|-----------|------|-------|
| `controlledProperty` | Property | `temperature` or `humidity` |
| `value` | Property | Number, with `unitCode` and `observedAt` |
| `minValue`, `maxValue` | Property | Number. Absent when there is no limit on that side |
| `status` | Property | `ok` or `alert` |
| `refShelf` | Relationship | Shelf |

```json
{
  "id": "urn:ngsi-ld:Sensor:shelf-humidity",
  "type": "Sensor",
  "controlledProperty": {"type": "Property", "value": "humidity"},
  "value": {"type": "Property", "value": 72.0, "unitCode": "P1", "observedAt": "2026-11-12T14:00:00Z"},
  "maxValue": {"type": "Property", "value": 60.0},
  "status": {"type": "Property", "value": "alert"},
  "refShelf": {"type": "Relationship", "object": "urn:ngsi-ld:Shelf:1"}
}
```

### Alert

Created by the simulator when a reading crosses a limit. Inspired by the FIWARE Smart Data Model `Alert`.

| Attribute | Type | Value |
|-----------|------|-------|
| `category` | Property | `environment` |
| `subCategory` | Property | `temperature` or `humidity` |
| `refSensor` | Relationship | Sensor |
| `value` | Property | Number, the reading that crossed the limit |
| `threshold` | Property | Number, the limit crossed |
| `dateIssued` | Property | Time |
| `acknowledgedBy` | Property | Name of the technician informed. Absent until acknowledged |
| `acknowledgedAt` | Property | Time. Absent until acknowledged |

An alert is active while it has no `acknowledgedBy`.

### Robot

| Attribute | Type | Value |
|-----------|------|-------|
| `state` | Property | `idle`, `busy` or `error` |
| `refTask` | Relationship | Task being run. Absent when idle |

### Task

One per robot task, created when the task starts and updated when it ends. The key is the `task_id` of the [robot command](../robot-command/).

| Attribute | Type | Value |
|-----------|------|-------|
| `action` | Property | `store`, `retrieve` or `home` |
| `refPartType` | Relationship | PartType. Absent for `home` |
| `refSlot` | Relationship | Slot. Absent for `home` |
| `status` | Property | `queued`, `running`, `succeeded`, `failed` or `stopped` |
| `failure` | Property | Failure code of the robot command. Absent unless `failed` |
| `attempts` | Property | Integer |
| `partLocation` | Property | `slot`, `tray`, `gripper` or `unknown`. Absent for `home` |
| `confirmedBy` | Property | Technician who approved the action |
| `startedAt`, `finishedAt` | Property | Time. `finishedAt` absent while running |

## Mapping to the MCP tools

The twin server turns entities into the [MCP outputs](../mcp/#twin-server):

| MCP field | NGSI-LD |
|-----------|---------|
| `Part.part` | Key of the PartType id |
| `Part.names` | `PartType.name` |
| `Part.stock`, `Part.slots` | Slots with `refPartType` pointing to the PartType |
| `Part.threshold` | `PartType.stockThreshold` |
| `Slot.part`, `tray.part` | Key of `refPartType`, null when absent |
| `Sensor.sensor`, `kind`, `min`, `max` | Key of the Sensor id, `controlledProperty`, `minValue`, `maxValue` |
| `Sensor.value`, `unit`, `observed_at` | `value` with its `unitCode` and `observedAt` |
| `Alert.sensor`, `kind`, `limit`, `raised_at` | Key of `refSensor`, `subCategory`, `threshold`, `dateIssued` |
| `PurchaseOrder.part`, `supplier` | Key of `refPartType`, `name` of the Supplier |
| `Task.part`, `slot` | Keys of `refPartType` and `refSlot` |

## Common queries

```
GET /ngsi-ld/v1/entities?type=Slot&q=refPartType=="urn:ngsi-ld:PartType:propeller"   stock and slots of a part
GET /ngsi-ld/v1/entities?type=Slot&q=!refPartType                                      free slots
GET /ngsi-ld/v1/entities?type=Alert&q=!acknowledgedBy                                  active alerts
GET /ngsi-ld/v1/entities?type=PurchaseOrder&q=status=="ordered"                        open orders
```

Add `options=keyValues` for values without the NGSI-LD wrapping.

Subscriptions (`POST /ngsi-ld/v1/subscriptions`) notify a service when an entity changes, e.g. the interface on a new `Alert` or a change of `Slot`. Each block creates the subscriptions it needs at startup.

## Seed

```sh
python contracts/ngsi-ld/seed.py      # Orion-LD at ORION_URL, default http://localhost:1026
```

Deletes every entity of the types above, then loads the starting state and prints the stock per part, the free slots and the active alerts. No dependencies.
