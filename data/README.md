# Data formats â€” proposed for Adrien review

## Mechanical BOM

[OpenROV CSV](openrov/derived/bom.csv): UTF-8, comma delimiter, header row, one row per mechanical part type. Quantities are integer occurrences in the full CAD assembly, not purchasing quantities.

| Column | Meaning |
|---|---|
| `part_id` | Stable project PartType key; selected types keep OR28-COLLAR, OR28-MOTOR-MOUNT and OR28-SERVO-MOUNT |
| `bom_ref` | Same project key, mapped to twin `bomRef`; not an original supplier reference |
| `name_en` | Original CAD name |
| `name_fr` | French translation prepared for INTELLIWARE |
| `parent_assembly` | OR28: whole OpenROV 2.8, flattened; not the immediate subassembly |
| `quantity` | Count in the source CAD assembly |
| `source_url` | Frozen upstream source |

IDs must be unique, quantities positive integers and fields nonempty. The IDs map to `urn:ngsi-ld:PartType:<part_id>` and the `bomRef` attribute in the [NGSI-LD contract](../contracts/ngsi-ld/README.md). The final values still require agreement with Adrien; this change does not alter the current seed data. No supplier, price or order reference is invented.

## Procedures

Use [TEMPLATE.md](procedures/TEMPLATE.md): title, language, part IDs, sources, numbered steps and validation status. Write the future procedures in French; keep unverified drafts clearly marked. Source references must support each step.

**Status:** CSV and template prepared. Adrien approval pending. [Sources and licenses](openrov/README.md).
