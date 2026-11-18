# Data

| Folder | Content | License |
|--------|---------|---------|
| [openrov](openrov/) | Public OpenROV BOM and manuals | Original license, kept in the folder |
| [procedures](procedures/) | Maintenance procedures written by us (French) | MIT |

Third-party files keep their source and LICENSE in their folder ([CONTRIBUTING.md](../CONTRIBUTING.md#third-party-files)). Robot demonstrations are not stored in Git: they go to Hugging Face Hub (LeRobot format).

## Proposed formats for Adrien review

### Mechanical BOM

[OpenROV CSV](openrov/derived/bom.csv): UTF-8, comma delimiter, header row, one row per mechanical part type. Quantities are integer occurrences in the full CAD assembly, not purchasing quantities. The 36 source leaf types become 34 rows after grouping the forward endcap's three layer types into one replaceable assembly.

| Column | Meaning |
|---|---|
| `part_id` | Project PartType key used in robot instructions; selected types: `endcap`, `collar`, `twist-lock`. Other rows keep their existing keys |
| `bom_ref` | Project BOM reference mapped to twin `bomRef`, such as `OR28-COLLAR`; not an original supplier reference |
| `name_en` | Original CAD name, or the documented grouped assembly name |
| `name_fr` | French translation prepared for INTELLIWARE |
| `parent_assembly` | OR28: whole OpenROV 2.8, flattened; not the immediate subassembly |
| `quantity` | Count in the source CAD assembly |
| `source_url` | Frozen upstream source |

IDs must be unique, quantities positive integers and fields nonempty. The IDs map to `urn:ngsi-ld:PartType:<part_id>` and the `bomRef` attribute in the [NGSI-LD contract](../contracts/ngsi-ld/README.md). The final values still require agreement with Adrien; this change does not alter the current seed data. No supplier, price or order reference is invented.

The `endcap` row (`OR28-FORWARD-ENDCAP`, quantity 2) groups, per endcap: two `Forward Endcap 3mm`, one `Forward Endcap 6mm` and one `Forward Endcap Outer`. Their former whole-vehicle counts were 4, 2 and 2. These layer rows are replaced, not counted again. The collar and twist-lock handling replicas in [#42](https://github.com/flodufour/INTELLIWARE/pull/42) are thickened to 18 mm; this CSV retains their source names and vehicle quantities, not a claim of original replica thickness. Florian will update seed and examples after acceptance.

### Procedures

Use [TEMPLATE.md](procedures/TEMPLATE.md): title, language, part IDs, sources, numbered steps and validation status. Write the future procedures in French; keep unverified drafts clearly marked. Source references must support each step.

**Status:** CSV and template prepared. Adrien approval pending. [Sources and licenses](openrov/README.md).
