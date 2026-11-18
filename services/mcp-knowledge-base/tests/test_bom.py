"""CSV validation and integration checks for the knowledge graph importer."""

import csv
import os
import uuid

import pytest
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from mcp_knowledge_base.bom import load_bom, read_bom

FIELDS = ["part_id", "bom_ref", "name_en", "name_fr", "parent_assembly", "quantity", "source_url"]


def write_csv(path, rows, fields=FIELDS):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.fixture
def sample_rows():
    # Synthetic fixtures, not a copy of the upstream mechanical BOM.
    return [
        {"part_id": part, "bom_ref": f"TEST-{part.upper()}", "name_en": part,
         "name_fr": name, "parent_assembly": "TEST-ASSEMBLY", "quantity": str(quantity),
         "source_url": "https://example.org/test-bom"}
        for part, name, quantity in [("endcap", "bouchon", 2), ("collar", "collier", 3),
                                     ("twist-lock", "verrou tournant", 4)]
    ]


def test_read_bom_preserves_identifiers_names_and_assembly_quantities(tmp_path, sample_rows):
    rows = read_bom(write_csv(tmp_path / "bom.csv", sample_rows))
    assert [row["part_id"] for row in rows] == ["endcap", "collar", "twist-lock"]
    assert rows[0]["bom_ref"] == "TEST-ENDCAP"
    assert rows[0]["name_fr"] == "bouchon"
    assert [row["quantity"] for row in rows] == [2, 3, 4]
    assert all(row["parent_assembly"] == "TEST-ASSEMBLY" for row in rows)


@pytest.mark.parametrize("quantity", ["0", "-1", "1.5", "two", ""])
def test_reject_nonpositive_or_noninteger_quantities(tmp_path, sample_rows, quantity):
    sample_rows[0]["quantity"] = quantity
    with pytest.raises(ValueError):
        read_bom(write_csv(tmp_path / "bom.csv", sample_rows))


@pytest.mark.parametrize("key", ["part_id", "bom_ref"])
def test_reject_duplicate_keys(tmp_path, sample_rows, key):
    sample_rows[1][key] = sample_rows[0][key]
    with pytest.raises(ValueError, match="duplicate"):
        read_bom(write_csv(tmp_path / "bom.csv", sample_rows))


def test_reject_empty_required_field(tmp_path, sample_rows):
    sample_rows[1]["name_fr"] = "  "
    with pytest.raises(ValueError, match="every column"):
        read_bom(write_csv(tmp_path / "bom.csv", sample_rows))


@pytest.mark.parametrize("content", ["", ",".join(FIELDS) + "\n", "part_id,quantity\ncap,2\n"])
def test_reject_missing_header_rows_or_columns(tmp_path, content):
    path = tmp_path / "bom.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        read_bom(path)


def test_reject_extra_column_values(tmp_path, sample_rows):
    path = write_csv(tmp_path / "bom.csv", sample_rows)
    with path.open("a", encoding="utf-8") as file:
        file.write("bad,ref,name,nom,assembly,2,https://example.org,extra\n")
    with pytest.raises(ValueError, match="every column"):
        read_bom(path)


@pytest.fixture
def graph(tmp_path, sample_rows):
    uri = os.environ.get("NEO4J_TEST_URI")
    if not uri:
        pytest.skip("Set NEO4J_TEST_URI to run Neo4j integration tests")
    prefix = f"bom-test-{uuid.uuid4().hex}-"
    for row in sample_rows:
        for key in ("part_id", "bom_ref", "parent_assembly"):
            row[key] = prefix + row[key]
    path = write_csv(tmp_path / "bom.csv", sample_rows)
    auth = (os.environ.get("NEO4J_USERNAME", "neo4j"),
            os.environ.get("NEO4J_PASSWORD", "intelliware-dev"))
    with GraphDatabase.driver(uri, auth=auth) as driver:
        driver.verify_connectivity()
        try:
            yield driver, path, sample_rows, prefix
        finally:
            driver.execute_query(
                "MATCH (p:PartType) WHERE p.part_id STARTS WITH $prefix DETACH DELETE p",
                prefix=prefix, database_="neo4j",
            )
            driver.execute_query(
                "MATCH (a:Assembly) WHERE a.assembly_id STARTS WITH $prefix DETACH DELETE a",
                prefix=prefix, database_="neo4j",
            )


def graph_rows(driver, prefix):
    records, _, _ = driver.execute_query(
        "MATCH (a:Assembly)-[r:HAS_PART]->(p:PartType) "
        "WHERE a.assembly_id STARTS WITH $prefix "
        "RETURN a.assembly_id AS assembly, p.part_id AS part, p.bom_ref AS bom_ref, "
        "p.name_en AS name_en, p.name_fr AS name_fr, p.source_url AS source_url, "
        "r.quantity AS quantity ORDER BY part",
        prefix=prefix, database_="neo4j",
    )
    return [record.data() for record in records]


@pytest.mark.neo4j
def test_import_all_types_and_reload_without_duplicates(graph):
    driver, path, rows, prefix = graph
    assert load_bom(driver, path) == 3
    first = graph_rows(driver, prefix)
    assert load_bom(driver, path) == 3
    assert graph_rows(driver, prefix) == first
    assert len(first) == 3
    for row in rows:
        actual = next(part for part in first if part["part"] == row["part_id"])
        assert actual == {
            "assembly": row["parent_assembly"], "part": row["part_id"], "bom_ref": row["bom_ref"],
            "name_en": row["name_en"], "name_fr": row["name_fr"], "source_url": row["source_url"],
            "quantity": int(row["quantity"]),
        }


@pytest.mark.neo4j
def test_reload_updates_bom_without_erasing_other_knowledge(graph):
    driver, path, rows, prefix = graph
    load_bom(driver, path)
    driver.execute_query(
        "MATCH (p:PartType {part_id: $part}) SET p.storage_note = 'keep me' "
        "CREATE (:Assembly {assembly_id: $assembly})-[:HAS_PART {quantity: 8}]->(p)",
        part=rows[0]["part_id"], assembly=prefix + "other", database_="neo4j",
    )
    rows[0]["quantity"] = "7"
    rows[0]["name_fr"] = "bouchon révisé"
    load_bom(driver, write_csv(path, rows))
    records, _, _ = driver.execute_query(
        "MATCH (a:Assembly)-[r:HAS_PART]->(p:PartType {part_id: $part}) "
        "RETURN a.assembly_id AS assembly, r.quantity AS quantity, "
        "p.name_fr AS name_fr, p.storage_note AS note ORDER BY assembly",
        part=rows[0]["part_id"], database_="neo4j",
    )
    by_assembly = {record["assembly"]: record.data() for record in records}
    assert by_assembly[rows[0]["parent_assembly"]]["quantity"] == 7
    assert by_assembly[prefix + "other"]["quantity"] == 8
    assert all(record["note"] == "keep me" and record["name_fr"] == "bouchon révisé" for record in records)


@pytest.mark.neo4j
def test_invalid_csv_leaves_existing_graph_unchanged(graph):
    driver, path, rows, prefix = graph
    load_bom(driver, path)
    before = graph_rows(driver, prefix)
    rows.append(rows[0].copy())
    with pytest.raises(ValueError, match="duplicate"):
        load_bom(driver, write_csv(path, rows))
    assert graph_rows(driver, prefix) == before


@pytest.mark.neo4j
def test_database_conflict_rolls_back_all_bom_rows(graph):
    driver, path, rows, prefix = graph
    driver.execute_query(
        "CREATE (:PartType {part_id: $part, bom_ref: $bom_ref})",
        part=prefix + "blocker", bom_ref=rows[1]["bom_ref"], database_="neo4j",
    )
    with pytest.raises(Neo4jError):
        load_bom(driver, path)
    assert graph_rows(driver, prefix) == []
    records, _, _ = driver.execute_query(
        "MATCH (p:PartType) WHERE p.part_id STARTS WITH $prefix RETURN count(p) AS count",
        prefix=prefix, database_="neo4j",
    )
    assert records[0]["count"] == 1
