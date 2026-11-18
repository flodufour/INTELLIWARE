"""Neo4j-backed MCP checks with isolated, synthetic BOM fixtures."""

import asyncio
import json
import os
import uuid

import pytest
from intelliware_mcp_contracts.models import PartInfo
from mcp import Client
from neo4j import GraphDatabase

from mcp_knowledge_base.server import create_server


@pytest.fixture
def graph():
    uri = os.environ.get("NEO4J_TEST_URI")
    if not uri:
        pytest.skip("Set NEO4J_TEST_URI for dedicated Neo4j integration tests")
    prefix = f"mcp-test-{uuid.uuid4().hex}-"
    part = prefix + "endcap"
    auth = (os.environ.get("NEO4J_USERNAME", "neo4j"), os.environ.get("NEO4J_PASSWORD", "intelliware-dev"))
    with GraphDatabase.driver(uri, auth=auth) as driver:
        driver.execute_query(
            "CREATE (a:Assembly {assembly_id: $assembly}) "
            "CREATE (p:PartType {part_id: $part, bom_ref: $bom_ref, name_en: 'endcap', "
            "name_fr: 'bouchon', source_url: 'https://example.org/test-bom'}) "
            "CREATE (a)-[:HAS_PART {quantity: 2}]->(p)",
            assembly=prefix + "OR28", part=part, bom_ref=prefix + "BOM", database_="neo4j",
        )
        try:
            yield driver, uri, prefix, part
        finally:
            driver.execute_query(
                "MATCH (n) WHERE n.part_id STARTS WITH $prefix OR n.assembly_id STARTS WITH $prefix "
                "OR n.test_id STARTS WITH $prefix DETACH DELETE n",
                prefix=prefix, database_="neo4j",
            )


def fetch(uri, part, endpoint=None):
    async def run():
        async with Client(endpoint or create_server(uri=uri), cache=None) as client:
            return await client.call_tool("get_part_info", {"part": part})
    return asyncio.run(run())


@pytest.mark.knowledge
def test_get_part_info_reads_the_real_bom_graph(graph):
    _, uri, prefix, part = graph
    result = fetch(uri, part)
    assert not result.is_error
    info = PartInfo.model_validate(result.structured_content)
    assert (info.part, info.names.fr, info.assembly) == (part, "bouchon", prefix + "OR28")
    assert info.storage.humidity_max is None
    assert info.documents[0].document == "https://example.org/test-bom"


@pytest.mark.knowledge
def test_changed_graph_metadata_is_visible_without_restarting(graph):
    driver, uri, _, part = graph

    async def run():
        async with Client(create_server(uri=uri), cache=None) as client:
            before = await client.call_tool("get_part_info", {"part": part})
            driver.execute_query("MATCH (p:PartType {part_id: $part}) SET p.name_fr = 'bouchon révisé'",
                                 part=part, database_="neo4j")
            after = await client.call_tool("get_part_info", {"part": part})
            assert PartInfo.model_validate(before.structured_content).names.fr == "bouchon"
            assert PartInfo.model_validate(after.structured_content).names.fr == "bouchon révisé"
    asyncio.run(run())


@pytest.mark.knowledge
def test_explicit_relationships_and_limits_are_returned(graph):
    driver, uri, prefix, part = graph
    driver.execute_query(
        "MATCH (p:PartType {part_id: $part}) SET p.storage_humidity_max = 61 "
        "CREATE (child:PartType {part_id: $child}), (seal:PartType {part_id: $seal}) "
        "CREATE (p)-[:HAS_PART]->(child), (p)-[:RELATED_TO]->(seal) "
        "CREATE (p)-[:HAS_PROCEDURE]->(:Procedure {test_id: $test, procedure_id: 'PROC-TEST'}) "
        "CREATE (p)-[:DOCUMENTED_IN {section: 'Test'}]->(:Document {test_id: $test, document: 'test.md'})",
        part=part, child=prefix + "child", seal=prefix + "seal", test=prefix + "metadata", database_="neo4j",
    )
    info = PartInfo.model_validate(fetch(uri, part).structured_content)
    assert info.subparts == [prefix + "child"] and info.related_parts == [prefix + "seal"]
    assert info.procedures == ["PROC-TEST"]
    assert any(document.document == "test.md" and document.section == "Test" for document in info.documents)
    assert info.storage.humidity_max == 61 and info.storage.temperature_min is None


@pytest.mark.knowledge
def test_unknown_and_query_like_part_keys_are_not_found(graph):
    _, uri, _, part = graph
    result = fetch(uri, part + "'}) MATCH (n) RETURN n //")
    assert result.is_error and json.loads(result.content[0].text)["error"] == "not_found"
    assert not fetch(uri, part).is_error


@pytest.mark.knowledge
def test_real_streamable_http_endpoint(graph):
    endpoint = os.environ.get("MCP_KNOWLEDGE_BASE_TEST_URL")
    if not endpoint:
        pytest.skip("Set MCP_KNOWLEDGE_BASE_TEST_URL to include the real HTTP endpoint")
    _, uri, _, part = graph
    result = fetch(uri, part, endpoint)
    assert not result.is_error
    assert PartInfo.model_validate(result.structured_content).part == part
