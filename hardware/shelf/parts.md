# Three OpenROV handling replicas

| PartType key | BOM reference | Export envelope (mm) | Shape and adaptation | Models |
|---|---|---|---|---|
| `endcap` | `OR28-FORWARD-ENDCAP` | 40 x 45.67 x 15 | Stepped forward endcap; original layers fused at their CAD positions | [STEP](../../data/openrov/derived/printable/or28-endcap.step), [STL](../../data/openrov/derived/printable/or28-endcap.stl) |
| `collar` | `OR28-COLLAR` | 40 x 38.80 x 18 | Ring; original XY contour, thickness increased from 6 to 18 mm | [STEP](../../data/openrov/derived/printable/or28-collar.step), [STL](../../data/openrov/derived/printable/or28-collar.stl) |
| `twist-lock` | `OR28-TWIST-LOCK` | 50 x 21.92 x 18 | Open fork; original XY contour, thickness increased from 6 to 18 mm | [STEP](../../data/openrov/derived/printable/or28-twist-lock.step), [STL](../../data/openrov/derived/printable/or28-twist-lock.stl) |

All envelope dimensions are between 15 and 60 mm. These are proposed dry handling replicas; the two thickened parts are deliberately modified, not original-size replacement spares. Grip and camera recognition remain untested. Quantities in the [mechanical BOM](../../data/openrov/derived/bom.csv) are two of each on the source vehicle, not shelf stock. Merge after [#41](https://github.com/flodufour/INTELLIWARE/pull/41), which provides the matching keys and CSV.

## Measurements and construction

Source: [OpenROV 2.8 STEP files](https://github.com/OpenROV/openrov-hardware/tree/1268e948fb9c60c38a0b1f7c6450b466558e7342/CAD_Files_OpenROV_v2_8/STEP) at frozen revision `1268e948fb9c60c38a0b1f7c6450b466558e7342`. Envelopes measured from solids in millimetres, preserving source assembly placements for stacked parts.

| Candidate | Measured source envelope (mm) | Decision |
|---|---|---|
| Battery aft endcap: Inner + Middle + Outer | 40 x 40 x 12 | Too thin; do not select a second endcap |
| Forward endcap: 2 x 3mm + 6mm + Outer | 40 x 45.67 x 15, in assembled orientation | Keep; four layers form one solid |
| NPT / PT gland: Inner + Middle + Outer | 94 mm diameter, 10.5 mm stacked thickness | Too wide and too thin; not a small tether fitting |
| Battery Tube Collar | 40 x 38.80 x 6 | Keep profile, thicken to 18 mm |
| Twist Lock | 50 x 21.92 x 6 | Keep profile, thicken to 18 mm |

The endcap uses two `Forward Endcap 3mm` occurrences, one `Forward Endcap 6mm` and one `Forward Endcap Outer` from `Battery Tubes/Battery Tube Assembly.stp`. Fuse without scaling; rotate to place the outer flange on the bed. For collar and twist-lock, fuse three copies of the original flat solid at Z offsets 0, 6 and 12 mm. All exports have minimum XYZ at zero, with thickness along Z.

Validation: each STEP is one valid solid, round-trip volume error below 0.01 mm3; each STL is watertight, with envelope error below 0.03 mm and volume error below 0.03%. Geometry checks do not establish printability or grasp success.

## Print and robot check before 2026-11-27

Import the three STL files into Bambu Studio in millimetres at 100%. Select the actual printer, nozzle and material. Inspect layer previews and support needs, especially the endcap groove/overhang. Print one of each first.

- [ ] Measure printed envelopes and confirm finger contact/clearance on the actual PIPER (70 mm opening is still an assumption).
- [ ] Test picks and placements with each part in a bin and the I/O tray, including both lower shelf bins; record failures and a short video.
- [ ] Check fixed-camera distinction between the shapes and empty/occupied bins before recording demonstrations. If lying-flat picks fail, try an on-edge holder and retest.

No print or physical test is claimed. OpenROV and contributors: [CC BY-NC-SA 4.0](../../data/openrov/derived/LICENSE.txt). INTELLIWARE's fused/thickened derivatives retain that license; they are not certified for underwater use.
