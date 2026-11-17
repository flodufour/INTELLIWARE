# Three selected OpenROV 2.8 parts

| Project ID | Source CAD name | Envelope (mm) | CAD quantity | Models |
|---|---|---|---|---|
| OR28-COLLAR | Battery Tube Collar | 40 × 38.8 × 6 | 2 | [STEP](../../data/openrov/derived/printable/or28-collar.step), [STL](../../data/openrov/derived/printable/or28-collar.stl) |
| OR28-MOTOR-MOUNT | Vert Moto Mount | 32 × 59 × 6 | 1 | [STEP](../../data/openrov/derived/printable/or28-motor-mount.step), [STL](../../data/openrov/derived/printable/or28-motor-mount.stl) |
| OR28-SERVO-MOUNT | Electronics Chassis Servo Mount | 15.5 × 56.5 × 6 | 1 | [STEP](../../data/openrov/derived/printable/or28-servo-mount.step), [STL](../../data/openrov/derived/printable/or28-servo-mount.stl) |

Source: [OpenROV 2.8 CAD at the frozen revision](https://github.com/OpenROV/openrov-hardware/tree/1268e948fb9c60c38a0b1f7c6450b466558e7342/CAD_Files_OpenROV_v2_8). All three appear in the [mechanical BOM](../../data/openrov/derived/bom.csv). Quantities describe the original vehicle, not shelf inventory.

Selection: different shapes, small dimensions and available CAD. Assumed gripper opening: 70 mm; actual gripping and visual recognition remain untested. The servo width is its overall envelope, not the width of its thin gripping web. Trial supports may be needed for finger clearance.

Import STL into Bambu Studio in millimetres at 100%. Select the actual printer, nozzle and material before slicing. Replicas are for dry handling demonstrations, not certified underwater use. OpenROV and contributors retain [CC BY-NC-SA 4.0](../../data/openrov/derived/LICENSE.txt).
