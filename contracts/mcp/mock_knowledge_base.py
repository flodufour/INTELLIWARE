# /// script
# requires-python = ">=3.12"
# dependencies = ["mcp>=2.3,<3"]
# ///
"""Mock knowledge base MCP server (README.md). Keyword search on fixed chunks.

Run: uv run mock_knowledge_base.py
"""

import os

from mcp.server.mcpserver import MCPServer

from models import Chunks, PartInfo, Procedure, fail

PROCEDURES = {
    "PROC-THRUSTER-01": {
        "procedure_id": "PROC-THRUSTER-01",
        "title": "Propulseur qui vibre : diagnostic",
        "language": "fr",
        "steps": [
            "Couper l'alimentation du véhicule.",
            "Vérifier que l'hélice n'est ni fissurée ni déformée.",
            "Vérifier le serrage de l'hélice sur l'axe moteur.",
            "Remplacer l'hélice si elle est endommagée.",
        ],
        "parts": ["propeller"],
        "document": "procedures/thruster.md",
    },
    "PROC-PROPELLER-02": {
        "procedure_id": "PROC-PROPELLER-02",
        "title": "Remplacement de l'hélice",
        "language": "fr",
        "steps": [
            "Couper l'alimentation du véhicule.",
            "Dévisser l'écrou de l'hélice.",
            "Retirer l'hélice usagée et monter l'hélice neuve.",
            "Resserrer l'écrou et tester le propulseur à basse vitesse.",
        ],
        "parts": ["propeller"],
        "document": "procedures/propeller.md",
    },
}
CHUNKS = [
    {"chunk_id": "c1", "text": "Si le propulseur vibre, vérifier l'hélice : fissure, déformation, serrage.",
     "document": "procedures/thruster.md", "section": "Diagnostic", "kind": "procedure", "language": "fr",
     "procedure_id": "PROC-THRUSTER-01", "keywords": {"thruster", "vibrate", "vibrates", "propulseur", "vibre"}},
    {"chunk_id": "c2", "text": "Pour remplacer l'hélice, dévisser l'écrou, monter l'hélice neuve, resserrer.",
     "document": "procedures/propeller.md", "section": "Remplacement", "kind": "procedure", "language": "fr",
     "procedure_id": "PROC-PROPELLER-02", "keywords": {"propeller", "replace", "hélice", "remplacer"}},
    {"chunk_id": "c3", "text": "The battery tube end caps seal the electronics. Inspect O-rings before each dive.",
     "document": "openrov/manual.pdf", "section": "Battery tubes", "kind": "manual", "language": "en",
     "procedure_id": None, "keywords": {"battery", "cap", "seal", "o-ring", "batterie", "bouchon"}},
]
PARTS = {
    "propeller": {"part": "propeller", "names": {"en": "propeller", "fr": "hélice"}, "assembly": "thruster",
                  "subparts": [], "related_parts": [],
                  "documents": [{"document": "procedures/propeller.md", "section": "Remplacement"}],
                  "procedures": ["PROC-THRUSTER-01", "PROC-PROPELLER-02"],
                  "storage": {"temperature_min": 5.0, "temperature_max": 40.0, "humidity_max": 80.0}},
    "cap": {"part": "cap", "names": {"en": "battery tube cap", "fr": "bouchon de tube batterie"},
            "assembly": "battery tube", "subparts": [], "related_parts": [],
            "documents": [{"document": "openrov/manual.pdf", "section": "Battery tubes"}], "procedures": [],
            "storage": {"temperature_min": 5.0, "temperature_max": 30.0, "humidity_max": 60.0}},
    "clip": {"part": "clip", "names": {"en": "cable clip", "fr": "clip de câble"}, "assembly": "tether",
             "subparts": [], "related_parts": [], "documents": [], "procedures": [],
             "storage": {"temperature_min": 0.0, "temperature_max": 40.0, "humidity_max": 80.0}},
}

server = MCPServer("knowledge-base", instructions="OpenROV documentation, BOM and maintenance procedures.")


@server.tool()
def search_documents(query: str, limit: int = 5) -> Chunks:
    """Search manuals, procedures and standards, in French or English."""
    words = set(query.lower().replace("?", " ").replace(",", " ").split())
    scored = []
    for chunk in CHUNKS:
        hits = len(words & chunk["keywords"])
        if hits:
            result = {k: v for k, v in chunk.items() if k != "keywords"}
            scored.append({**result, "score": round(hits / len(words), 2)})
    scored.sort(key=lambda c: c["score"], reverse=True)
    return Chunks.model_validate({"chunks": scored[:limit]})


@server.tool()
def get_procedure(procedure_id: str) -> Procedure:
    """Full maintenance procedure with its steps and parts."""
    if procedure_id not in PROCEDURES:
        return fail("not_found", f"unknown procedure '{procedure_id}'")
    return Procedure.model_validate(PROCEDURES[procedure_id])


@server.tool()
def get_part_info(part: str) -> PartInfo:
    """BOM position, documents and storage conditions of a part type."""
    if part not in PARTS:
        return fail("not_found", f"unknown part '{part}'")
    return PartInfo.model_validate(PARTS[part])


if __name__ == "__main__":
    server.run("streamable-http", host=os.environ.get("HOST", "127.0.0.1"),
               port=int(os.environ.get("PORT", 8002)))
