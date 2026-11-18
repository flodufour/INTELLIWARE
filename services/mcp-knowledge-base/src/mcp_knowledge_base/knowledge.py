"""Read part metadata from the BOM graph defined by issue #48."""

from intelliware_mcp_contracts.models import DocumentRef, PartInfo, Storage
from neo4j import AsyncDriver, RoutingControl

QUERY = """
MATCH (p:PartType {part_id: $part})
RETURN p.part_id AS part, p.name_en AS name_en, p.name_fr AS name_fr,
       p.source_url AS source_url,
       [(a:Assembly)-[:HAS_PART]->(p) | a.assembly_id] AS assemblies,
       [(p)-[:HAS_PART]->(child:PartType) | child.part_id] AS subparts,
       [(p)-[:RELATED_TO]-(other:PartType) | other.part_id] AS related_parts,
       [(p)-[:HAS_PROCEDURE]->(proc:Procedure) | proc.procedure_id] AS procedures,
       [(p)-[ref:DOCUMENTED_IN]->(doc:Document) |
           {document: doc.document, section: coalesce(ref.section, '')}] AS documents,
       p.storage_temperature_min AS temperature_min,
       p.storage_temperature_max AS temperature_max,
       p.storage_humidity_max AS humidity_max
"""


class UnknownPart(LookupError):
    pass


def part_info(row: dict) -> PartInfo:
    assemblies = sorted(set(row["assemblies"]))
    if len(assemblies) > 1:
        raise ValueError("The part has ambiguous parent assemblies")
    documents = [DocumentRef.model_validate(document) for document in row["documents"]]
    if row.get("source_url"):
        source = DocumentRef(document=row["source_url"], section="")
        if source not in documents:
            documents.append(source)
    return PartInfo(
        part=row["part"], names={"en": row["name_en"], "fr": row["name_fr"]},
        assembly=assemblies[0] if assemblies else None,
        subparts=sorted(set(row["subparts"])), related_parts=sorted(set(row["related_parts"])),
        documents=documents, procedures=sorted(set(row["procedures"])),
        storage=Storage(temperature_min=row.get("temperature_min"),
                        temperature_max=row.get("temperature_max"), humidity_max=row.get("humidity_max")),
    )


class KnowledgeBase:
    def __init__(self, driver: AsyncDriver, database: str = "neo4j"):
        self.driver = driver
        self.database = database

    async def get_part_info(self, part: str) -> PartInfo:
        records, _, _ = await self.driver.execute_query(
            QUERY, part=part, database_=self.database, routing_=RoutingControl.READ,
        )
        if not records:
            raise UnknownPart(part)
        if len(records) != 1:
            raise ValueError("Part identifiers are not unique")
        return part_info(records[0].data())
