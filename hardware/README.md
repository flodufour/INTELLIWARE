# Hardware

Parts we design ourselves: shelf, tray, camera mounts. MIT license like the rest of the repository. Third-party CAD (OpenROV) goes to [data/openrov](../data/openrov/) with its original license.

| Folder | Content | Owner |
|--------|---------|-------|
| [shelf](shelf/) | Shelf and input/output tray | Antoine ([#14](https://github.com/flodufour/INTELLIWARE/issues/14)) |

## Rules

- **SolidWorks files cannot be merged.** Only the folder owner edits them; others ask through an issue.
- **Export on every change**: commit `.SLDPRT` / `.SLDASM` together with an up-to-date `.STEP` (opens without SolidWorks) and `.STL` (3D printing, previewed by GitHub).
- **Say what changed** in the commit message, since Git cannot show it: `feat: raise shelf level 2 by 3 cm`.
- **Size**: GitHub warns at 50 MB and rejects files over 100 MB. Above 50 MB, use Git LFS.
