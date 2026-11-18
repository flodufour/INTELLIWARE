"""Load the mechanical BOM into Neo4j without changing live inventory."""

import argparse
import csv
import os
from pathlib import Path

from neo4j import Driver, GraphDatabase, ManagedTransaction, unit_of_work
from neo4j.exceptions import DriverError, Neo4jError

COLUMNS = ["part_id", "bom_ref", "name_en", "name_fr", "parent_assembly", "quantity", "source_url"]
DEFAULT_BOM = Path("data/openrov/derived/bom.csv")
CONSTRAINTS = [
    "CREATE CONSTRAINT intelliware_part_id IF NOT EXISTS "
    "FOR (p:PartType) REQUIRE p.part_id IS UNIQUE",
    "CREATE CONSTRAINT intelliware_bom_ref IF NOT EXISTS "
    "FOR (p:PartType) REQUIRE p.bom_ref IS UNIQUE",
    "CREATE CONSTRAINT intelliware_assembly_id IF NOT EXISTS "
    "FOR (a:Assembly) REQUIRE a.assembly_id IS UNIQUE",
]


def read_bom(path: str | Path) -> list[dict]:
    """Validate the entire CSV before making any database changes."""
    rows = []
    part_ids, bom_refs = set(), set()
    with Path(path).open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"Expected CSV columns: {', '.join(COLUMNS)}")
        for row in reader:
            line = reader.line_num
            if set(row) != set(COLUMNS) or any(value is None or not value.strip() for value in row.values()):
                raise ValueError(f"Line {line}: every column must have a value")
            row = {key: value.strip() for key, value in row.items()}
            if not row["quantity"].isascii() or not row["quantity"].isdigit() or int(row["quantity"]) < 1:
                raise ValueError(f"Line {line}: quantity must be a positive integer")
            if row["part_id"] in part_ids or row["bom_ref"] in bom_refs:
                raise ValueError(f"Line {line}: duplicate part_id or bom_ref")
            part_ids.add(row["part_id"])
            bom_refs.add(row["bom_ref"])
            row["quantity"] = int(row["quantity"])
            rows.append(row)
    if not rows:
        raise ValueError("BOM must contain at least one part type")
    return rows


@unit_of_work(timeout=30)
def _write_bom(tx: ManagedTransaction, rows: list[dict]) -> int:
    result = tx.run(
        """
        UNWIND $rows AS row
        MERGE (a:Assembly {assembly_id: row.parent_assembly})
        MERGE (p:PartType {part_id: row.part_id})
        SET p.bom_ref = row.bom_ref, p.name_en = row.name_en,
            p.name_fr = row.name_fr, p.source_url = row.source_url
        MERGE (a)-[r:HAS_PART]->(p)
        SET r.quantity = row.quantity
        RETURN count(p) AS loaded
        """,
        rows=rows,
    )
    return result.single(strict=True)["loaded"]


def load_bom(driver: Driver, path: str | Path, database: str = "neo4j") -> int:
    """Upsert part metadata and BOM edges in one retriable data transaction."""
    rows = read_bom(path)
    with driver.session(database=database) as session:
        for constraint in CONSTRAINTS:
            session.run(constraint).consume()
        return session.execute_write(_write_bom, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", nargs="?", type=Path, default=DEFAULT_BOM)
    args = parser.parse_args()
    uri = os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687")
    auth = (
        os.environ.get("NEO4J_USERNAME", "neo4j"),
        os.environ.get("NEO4J_PASSWORD", "intelliware-dev"),
    )
    try:
        with GraphDatabase.driver(uri, auth=auth, connection_timeout=5, max_transaction_retry_time=15) as driver:
            count = load_bom(driver, args.csv, os.environ.get("NEO4J_DATABASE", "neo4j"))
    except (OSError, ValueError, csv.Error, Neo4jError, DriverError) as error:
        parser.exit(1, f"BOM import failed: {error}\n")
    print(f"Loaded {count} BOM rows into Neo4j.")


if __name__ == "__main__":
    main()
