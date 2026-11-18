"""Opt-in end-to-end MCP checks against a dedicated seeded Orion-LD."""

import asyncio
import importlib.util
import json
import os
from pathlib import Path
from urllib.parse import quote

import httpx2
import pytest
from intelliware_mcp_contracts.models import Part, Parts, Shelf
from mcp import Client


@pytest.mark.orion
def test_seeded_twin_over_streamable_http():
    endpoint = os.environ.get("MCP_TWIN_TEST_URL")
    orion_url = os.environ.get("ORION_TEST_URL")
    if not endpoint or not orion_url:
        pytest.skip("Set MCP_TWIN_TEST_URL and ORION_TEST_URL for dedicated live tests")
    seed_path = Path(__file__).resolve().parents[3] / "contracts/ngsi-ld/seed.py"
    spec = importlib.util.spec_from_file_location("twin_seed", seed_path)
    seed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seed)

    async def run():
        async with Client(endpoint, cache=None, read_timeout_seconds=15) as client:
            result = await client.call_tool("list_parts")
            assert not result.is_error
            parts = Parts.model_validate(result.structured_content).parts
            assert {part.part for part in parts} == set(seed.PARTS)
            for part in parts:
                en, fr, _, threshold = seed.PARTS[part.part]
                assert (part.names.en, part.names.fr, part.threshold) == (en, fr, threshold)
                assert part.slots == sorted(slot for slot, item in seed.SLOTS.items() if item == part.part)
                assert part.stock == len(part.slots)
            shelf = Shelf.model_validate((await client.call_tool("get_shelf")).structured_content)
            assert {slot.slot: slot.part for slot in shelf.slots} == seed.SLOTS
            assert shelf.tray.part is None
            missing = await client.call_tool("get_part", {"part": "unknown-test-part"})
            assert missing.is_error and json.loads(missing.content[0].text)["error"] == "not_found"

            # A robot-side write must be visible without restarting the MCP server.
            part = next(part for part in parts if part.stock)
            slot_id = f"urn:ngsi-ld:Slot:{part.slots[0]}"
            attrs = f"{orion_url.rstrip('/')}/ngsi-ld/v1/entities/{quote(slot_id, safe='')}/attrs"
            async with httpx2.AsyncClient(timeout=5) as http:
                (await http.delete(attrs + "/refPartType")).raise_for_status()
                try:
                    changed = await client.call_tool("get_part", {"part": part.part})
                    assert Part.model_validate(changed.structured_content).stock == part.stock - 1
                finally:
                    (await http.post(attrs, json={"refPartType": {
                        "type": "Relationship", "object": f"urn:ngsi-ld:PartType:{part.part}",
                    }})).raise_for_status()
    asyncio.run(run())
