"""Shared-model mapping and MCP protocol behavior without a database."""

import asyncio
import json

import pytest
from intelliware_mcp_contracts.models import PartInfo
from mcp import Client
from neo4j.exceptions import ServiceUnavailable

from mcp_knowledge_base.knowledge import UnknownPart, part_info
from mcp_knowledge_base.server import create_server


@pytest.fixture
def record():
    return {"part": "endcap", "name_en": "endcap", "name_fr": "bouchon",
            "source_url": "https://example.org/bom", "assemblies": ["OR28"],
            "subparts": [], "related_parts": [], "procedures": [], "documents": [],
            "temperature_min": None, "temperature_max": None, "humidity_max": None}


class Repository:
    def __init__(self, record, error=None):
        self.record = record
        self.error = error

    async def get_part_info(self, part):
        if self.error:
            raise self.error
        if part != self.record["part"]:
            raise UnknownPart(part)
        return part_info(self.record)


def call(repository, part="endcap"):
    async def run():
        async with Client(create_server(repository=repository), cache=None) as client:
            return await client.call_tool("get_part_info", {"part": part})
    return asyncio.run(run())


def test_bom_metadata_has_explicit_unknown_storage(record):
    result = call(Repository(record))
    assert not result.is_error
    info = PartInfo.model_validate(result.structured_content)
    assert info.part == "endcap" and info.names.fr == "bouchon" and info.assembly == "OR28"
    assert info.storage.model_dump() == {"temperature_min": None, "temperature_max": None, "humidity_max": None}
    assert info.documents[0].document == record["source_url"]
    assert info.procedures == [] and info.related_parts == [] and info.subparts == []


def test_recorded_storage_values_and_partial_unknowns_are_preserved(record):
    record.update(temperature_min=5, humidity_max=60)
    info = PartInfo.model_validate(call(Repository(record)).structured_content)
    assert info.storage.temperature_min == 5.0
    assert info.storage.humidity_max == 60.0
    assert info.storage.temperature_max is None


def test_metadata_collections_are_deduplicated(record):
    record.update(assemblies=["OR28", "OR28"], subparts=["clip", "clip"],
                  related_parts=["seal", "seal"], procedures=["PROC-1", "PROC-1"])
    info = part_info(record)
    assert info.subparts == ["clip"] and info.related_parts == ["seal"] and info.procedures == ["PROC-1"]


@pytest.mark.parametrize(("part", "code"), [("missing", "not_found"), ("", "invalid_argument"),
                                          (" endcap", "invalid_argument")])
def test_argument_errors_follow_the_contract(record, part, code):
    result = call(Repository(record), part)
    assert result.is_error
    assert json.loads(result.content[0].text)["error"] == code


@pytest.mark.parametrize("error", [ServiceUnavailable("offline"), ValueError("invalid graph data")])
def test_backend_failure_returns_unavailable(record, error):
    result = call(Repository(record, error))
    assert result.is_error
    assert json.loads(result.content[0].text)["error"] == "unavailable"


def test_ambiguous_parent_assemblies_return_unavailable(record):
    record["assemblies"] = ["OR28", "other"]
    result = call(Repository(record))
    assert result.is_error and json.loads(result.content[0].text)["error"] == "unavailable"


def test_tool_advertises_the_shared_nullable_storage_schema(record):
    async def run():
        async with Client(create_server(repository=Repository(record)), cache=None) as client:
            tools = (await client.list_tools()).tools
            assert [tool.name for tool in tools] == ["get_part_info"]
            assert tools[0].annotations.read_only_hint
            field = tools[0].output_schema["$defs"]["Storage"]["properties"]["humidity_max"]
            assert {option["type"] for option in field["anyOf"]} == {"number", "null"}
    asyncio.run(run())
