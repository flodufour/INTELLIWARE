# Basic upright shelf

Frame: **300 × 160 × 280 mm** (width × depth × height), 300 mm high including bins. Two shelf boards, two sides, a rear brace, four 120 × 120 × 20 mm open-top bins and one 140 × 140 × 20 mm I/O tray.

![Shelf](preview.png)

Open [Shelf_classic.SLDASM](solidworks/Shelf_classic.SLDASM) in SolidWorks 2026. Keep the assembly and its five `.SLDPRT` files together. Components are fixed in position; imported solids have no native sketch history. Panels are intended as 12 mm plywood; bins and tray are printed.

[Geometry and reach report](validation.json): five valid part types, ten non-interpenetrating components; STEP round trips and native assembly reopening checked. With the assumed robot base at (150, 0, 400) in the local X-width / Y-up / Z-front frame, the maximum assumed flange radius is 561.46 mm, within a 576 mm screening limit (626 mm nominal reach minus 50 mm reserve; 150 mm tool offset).

**Pending:** actual robot/tool dimensions, lower-shelf access, joint limits, collisions, fastening, stability and Florian review. The radial calculation does not validate a robot trajectory. Nothing has been fabricated or physically tested.
