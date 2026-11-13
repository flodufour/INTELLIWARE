"""Check Neo4j vector indexing with temporary data; standard library only.

Run after `docker compose up -d --wait neo4j`:
    python scripts/check_neo4j.py
Set NEO4J_HTTP_URL, NEO4J_USERNAME and NEO4J_PASSWORD for a custom instance.
"""

import base64
import json
import os
import sys
import urllib.error
import urllib.request
import uuid


def query(statement: str, parameters: dict | None = None) -> list[list]:
    base_url = os.environ.get("NEO4J_HTTP_URL", "http://127.0.0.1:7474").rstrip("/")
    username = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "intelliware-dev")
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    data = json.dumps({"statement": statement, "parameters": parameters or {}}).encode()
    request = urllib.request.Request(
        base_url + "/db/neo4j/query/v2", data=data,
        headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=70) as response:
        result = json.load(response)
    # Query API can report a Cypher error with an HTTP success status.
    if result.get("errors"):
        raise RuntimeError(json.dumps(result["errors"]))
    return result["data"]["values"]


def main() -> None:
    token = uuid.uuid4().hex
    label = f"IntelliwareVectorSmoke{token}"
    index = f"intelliware_vector_smoke_{token}"
    vector = [0.9, 0.1, 0.1]
    # Generated names isolate this run from existing data and concurrent checks.
    query(
        f"CREATE (:{label} {{part: $part, embedding: $vector}}), "
        f"(:{label} {{part: 'cap', embedding: [0.1, 0.9, 0.1]}})",
        {"part": "propeller", "vector": vector},
    )
    try:
        query(
            f"CREATE VECTOR INDEX {index} FOR (n:{label}) ON n.embedding "
            "OPTIONS {indexConfig: {`vector.dimensions`: 3, "
            "`vector.similarity_function`: 'cosine'}}"
        )
        query("CALL db.awaitIndex($name, 60)", {"name": index})
        rows = query(
            "CALL db.index.vector.queryNodes($name, 1, $vector) "
            "YIELD node, score RETURN node.part, score ORDER BY score DESC",
            {"name": index, "vector": vector},
        )
        if not rows or rows[0][0] != "propeller" or rows[0][1] < 0.99:
            raise RuntimeError(f"Unexpected nearest neighbor: {rows}")
        print(f"Vector index ONLINE; nearest part: {rows[0][0]}, score: {rows[0][1]:.3f}")
    finally:
        try:
            query(f"DROP INDEX {index} IF EXISTS")
        finally:
            query(f"MATCH (n:{label}) DELETE n")
    print("Temporary vector index and nodes removed.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError) as error:
        sys.exit(f"Neo4j check failed: {error}")
