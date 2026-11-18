"""Read the NGSI-LD contract from Orion-LD and map it to shared MCP models."""

from urllib.parse import quote

import httpx2
from intelliware_mcp_contracts.models import Part, Parts, Shelf, Slot, Tray


class UnknownPart(LookupError):
    pass


def key(entity_id: str, kind: str) -> str:
    prefix = f"urn:ngsi-ld:{kind}:"
    if not isinstance(entity_id, str) or not entity_id.startswith(prefix) or not entity_id[len(prefix):]:
        raise ValueError(f"Invalid {kind} relationship")
    return entity_id[len(prefix):]


class Orion:
    def __init__(self, client: httpx2.AsyncClient):
        self.client = client

    async def entities(self, kind: str) -> list[dict]:
        entities = []
        offset = 0
        while True:
            response = await self.client.get("/ngsi-ld/v1/entities", params={
                "type": kind, "options": "keyValues", "limit": 1000, "offset": offset,
            })
            response.raise_for_status()
            page = response.json()
            if not isinstance(page, list):
                raise ValueError("Expected an entity list")
            entities.extend(page)
            if len(page) < 1000:
                return entities
            offset += len(page)

    async def entity(self, kind: str, part: str) -> dict:
        entity_id = f"urn:ngsi-ld:{kind}:{part}"
        response = await self.client.get(
            "/ngsi-ld/v1/entities/" + quote(entity_id, safe=""), params={"options": "keyValues"},
        )
        if response.status_code == 404 and kind == "PartType":
            raise UnknownPart(part)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def part_view(entity: dict, slots: list[dict]) -> Part:
        occupied = sorted(key(slot["id"], "Slot") for slot in slots
                          if slot.get("refPartType") == entity["id"])
        return Part(part=key(entity["id"], "PartType"), names=entity["name"],
                    stock=len(occupied), threshold=entity["stockThreshold"], slots=occupied)

    async def list_parts(self) -> Parts:
        parts = await self.entities("PartType")
        slots = await self.entities("Slot")
        return Parts(parts=[self.part_view(part, slots) for part in sorted(parts, key=lambda p: p["id"])])

    async def get_part(self, part: str) -> Part:
        entity = await self.entity("PartType", part)
        # Filter by exact URN locally instead of interpolating user input into q.
        return self.part_view(entity, await self.entities("Slot"))

    async def get_shelf(self) -> Shelf:
        slots = await self.entities("Slot")
        tray = await self.entity("Tray", "1")
        return Shelf(
            slots=[Slot(slot=key(slot["id"], "Slot"), level=slot["level"],
                        part=key(slot["refPartType"], "PartType") if slot.get("refPartType") else None)
                   for slot in sorted(slots, key=lambda s: s["id"])],
            tray=Tray(part=key(tray["refPartType"], "PartType") if tray.get("refPartType") else None),
        )
