# OpenROV 2.8 — sources and decision

**GO: keep OpenROV for the handling demonstrator.** [Mechanical BOM CSV](derived/bom.csv): 34 part types from the 36 leaf types in the [original full assembly](https://github.com/OpenROV/openrov-hardware/blob/1268e948fb9c60c38a0b1f7c6450b466558e7342/CAD_Files_OpenROV_v2_8/STEP/Full%20Assembly.stp), with the forward endcap's layers grouped as documented in the [data contract](../README.md). CAD occurrence counts are not a complete procurement BOM. Source SHA-256: `d69be5551a9a8d2c94bd2bdea7a2ee9ec70ccfc12d2e137b068ea3f4263b2b24`. CSV and procedure format approval by Adrien remains pending.

## Findings, 2026-11-17

- [Original supplier spreadsheet](https://docs.google.com/spreadsheet/ccc?key=0Avf6fUwp9B3kdF9YQWxBTnZjZEVGZVQwY25EbnVyREE): CSV endpoint still returns HTTP 410. The tested exact-URL archive query returned no result; this does not prove that no copy exists.
- [Official controller 2.8 BOM](https://github.com/OpenROV/openrov-electronics/blob/080242a28b9d1204e8359c75b57ddb6db5e1d883/OpenROV%20Controller%202.8%20Final%20Data%20Pkg/OpenROV%20Controller%202.8%20BOM.xls): found, but covers the controller board only. It is linked, not redistributed; no explicit license file was found in that electronics repository.
- [Illustrated kit contents](https://www.sekidorc.com/pdf/OpenROV_2.8KitPartsManifest_en_170508.pdf): packing list, not a supplier BOM.
- [Illustrated 2.8 assembly guide, Japanese](https://www.sekidorc.com/pdf/OpenROV_AssemblyGuide_jp_v1.0_151203.pdf): accessible PDF. Linked only; its redistribution terms have not been established.

## Assembly and maintenance guides

| Guide | Archived original |
|---|---|
| Introduction | [Guide 0](https://web.archive.org/web/20210302080529/https://openrov.dozuki.com/Guide/Guide+0+-+Introduction/103) |
| Acrylic cementing | [Guide 1](https://web.archive.org/web/20200925111823/https://openrov.dozuki.com/Guide/Guide+1+-+Acrylic+Cementing/118) |
| Tube endcaps | [Guide 2](https://web.archive.org/web/20200925100641/https://openrov.dozuki.com/Guide/Guide+2+-+Electronics+Tube+Endcaps/119) |
| Electronics | [Guide 3](https://web.archive.org/web/20200809115915/https://openrov.dozuki.com/Guide/Guide+3+-+Electronics/120) |
| Wire routing | [Guide 4](https://web.archive.org/web/20200809120142/https://openrov.dozuki.com/Guide/Guide+4+-+Wire+Routing/123) |
| Finishing | [Guide 5](https://web.archive.org/web/20201128052927/https://openrov.dozuki.com/Guide/Guide+5+-+Finishing/121) |
| Operation and maintenance | [Operator manual](https://web.archive.org/web/20191214153724/https://openrov.dozuki.com/Guide/OpenROV+Operators+Manual/80) |

A sampled archived guide illustration was retrievable; a complete offline image collection was not recovered. The GitHub submission contains links to these guides. Full supplier sourcing remains incomplete.

## Attribution and license

Mechanical CAD and its derivatives: OpenROV and contributors, [CC BY-NC-SA 4.0](derived/LICENSE.txt), per the [upstream license grant](https://github.com/OpenROV/openrov-hardware/blob/1268e948fb9c60c38a0b1f7c6450b466558e7342/README.md). INTELLIWARE derived the CSV and prepared handling replicas in [#42](https://github.com/flodufour/INTELLIWARE/pull/42): a fused forward endcap at original scale, plus collar and twist-lock profiles thickened from 6 to 18 mm. Adaptations retain the same license. These files are not MIT.

The linked Dozuki guides retain their authors' CC BY-SA 3.0 license. Only links are included in the short submission. Do not apply their license to the Sekido PDFs or electronics files without evidence.
