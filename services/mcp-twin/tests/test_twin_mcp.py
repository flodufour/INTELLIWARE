"""Exercise the MCP protocol with controlled Orion-LD HTTP responses."""

import asyncio
import json
from urllib.parse import unquote

import httpx2
import pytest
from intelliware_mcp_contracts.models import Part, Parts, Shelf
from mcp import Client

from mcp_twin.orion import Orion
from mcp_twin.server import create_server


@pytest.fixture
def inventory():
    return {
        "PartType": [{"id": "urn:ngsi-ld:PartType:endcap", "name": {"en": "endcap", "fr": "bouchon"},
                      "stockThreshold": 3, "stock": 999}],
        "Slot": [{"id": "urn:ngsi-ld:Slot:A1", "level": 1, "refPartType": "urn:ngsi-ld:PartType:endcap"},
                 {"id": "urn:ngsi-ld:Slot:A2", "level": 1, "refPartType": "urn:ngsi-ld:PartType:endcap"},
                 {"id": "urn:ngsi-ld:Slot:B1", "level": 2}],
        "Tray": [{"id": "urn:ngsi-ld:Tray:1"}],
    }


def transport_for(inventory):
    def request(request):
        assert request.method == "GET"
        assert request.url.params["options"] == "keyValues"
        if request.url.path == "/ngsi-ld/v1/entities":
            entities = inventory[request.url.params["type"]]
            offset = int(request.url.params["offset"])
            limit = int(request.url.params["limit"])
            return httpx2.Response(200, json=entities[offset:offset + limit])
        entity_id = unquote(request.url.path.rsplit("/", 1)[1])
        for entities in inventory.values():
            for entity in entities:
                if entity["id"] == entity_id:
                    return httpx2.Response(200, json=entity)
        return httpx2.Response(404, json={"detail": "not found"})
    return httpx2.MockTransport(request)


def call(inventory, tool, args=None, transport=None):
    async def run():
        server = create_server("http://orion.test", transport=transport or transport_for(inventory))
        async with Client(server, cache=None) as client:
            return await client.call_tool(tool, args)
    return asyncio.run(run())


def test_lists_schema_and_read_only_tools():
    async def run():
        async with Client(create_server(), cache=None) as client:
            tools = (await client.list_tools()).tools
            assert {tool.name for tool in tools} == {"list_parts", "get_part", "get_shelf"}
            assert all(tool.output_schema and tool.annotations.read_only_hint for tool in tools)
    asyncio.run(run())


def test_list_parts_calculates_stock_from_slots(inventory):
    result = call(inventory, "list_parts")
    assert not result.is_error
    parts = Parts.model_validate(result.structured_content)
    assert parts.parts[0].stock == 2
    assert parts.parts[0].slots == ["A1", "A2"]
    assert parts.parts[0].names.fr == "bouchon"
    assert parts.parts[0].threshold == 3


def test_get_part_reads_live_state_on_each_call(inventory):
    async def run():
        async with Client(create_server("http://orion.test", transport=transport_for(inventory)), cache=None) as client:
            before = await client.call_tool("get_part", {"part": "endcap"})
            inventory["Slot"][0].pop("refPartType")
            after = await client.call_tool("get_part", {"part": "endcap"})
            assert Part.model_validate(before.structured_content).stock == 2
            assert Part.model_validate(after.structured_content).stock == 1
    asyncio.run(run())


def test_shelf_maps_absent_relationships_to_null(inventory):
    result = call(inventory, "get_shelf")
    shelf = Shelf.model_validate(result.structured_content)
    assert shelf.slots[0].part == "endcap"
    assert shelf.slots[2].part is None
    assert shelf.tray.part is None


def test_shelf_maps_occupied_tray(inventory):
    inventory["Tray"][0]["refPartType"] = "urn:ngsi-ld:PartType:endcap"
    assert Shelf.model_validate(call(inventory, "get_shelf").structured_content).tray.part == "endcap"


@pytest.mark.parametrize(("part", "code"), [("missing", "not_found"), ("", "invalid_argument"),
                                          (" endcap", "invalid_argument"), ('x";q=*', "not_found")])
def test_argument_and_not_found_errors_are_contract_json(inventory, part, code):
    result = call(inventory, "get_part", {"part": part})
    assert result.is_error
    assert json.loads(result.content[0].text)["error"] == code


@pytest.mark.parametrize("tool,args", [("list_parts", {}), ("get_part", {"part": "endcap"}), ("get_shelf", {})])
def test_backend_failures_return_unavailable(inventory, tool, args):
    transport = httpx2.MockTransport(lambda request: httpx2.Response(503))
    result = call(inventory, tool, args, transport)
    assert result.is_error
    assert json.loads(result.content[0].text)["error"] == "unavailable"


def test_invalid_backend_data_returns_unavailable(inventory):
    inventory["PartType"][0].pop("name")
    result = call(inventory, "list_parts")
    assert result.is_error
    assert json.loads(result.content[0].text)["error"] == "unavailable"


def test_paginates_large_entity_sets(inventory):
    inventory["PartType"] = [dict(inventory["PartType"][0], id=f"urn:ngsi-ld:PartType:p{i}") for i in range(1001)]

    async def run():
        async with httpx2.AsyncClient(base_url="http://orion.test", transport=transport_for(inventory)) as client:
            parts = await Orion(client).entities("PartType")
            assert len(parts) == 1001
            assert parts[-1]["id"] == "urn:ngsi-ld:PartType:p1000"
    asyncio.run(run())
