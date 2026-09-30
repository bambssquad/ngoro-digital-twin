# CAD 2D and drawing sheets

Revision 05 adds a read-only CAD and drawing workspace to the existing Three.js site. The building model, source drawing, and SketchUp deliverable are unchanged.

The DWG is exported from a working copy through the installed AutoCAD Core Console (`scripts/export_cad_source.ps1`). `scripts/build_drawing_viewer.py` uses ezdxf 1.4.4 to render source vectors including dimension blocks, text, hatches and inserted blocks. The manifest records source/model hashes. Infinite construction XLINE entities are excluded from the page extents; non-plot and hidden layers follow renderer visibility. Fonts can differ from original AutoCAD fonts.

Install the generator dependency in the project only:
```
python -m pip install --target verification/cad-runtime ezdxf==1.4.4
python scripts/build_drawing_viewer.py
```

There are seven source views (all Model Space, siteplan, layout, foundations, columns, roof and transverse frame) and five model-derived sheets (clean plan with section lines, two orthographic elevations and two sections). Original paper layouts are empty, so the source views are crops of Model Space, not original plotted sheets. Source annotations are preserved. Derived sheets are visual coordination studies from model revision 04; they do not claim fabrication or structural design approval.

`drawings.js` lazy-loads versioned SVG assets when a drawing mode is opened. Each vector path carries a layer label for visibility controls. Pan uses pointer capture; zoom supports wheel, buttons and two-pointer pinch. Keyboard arrows pan, +/- zoom and Home fits the sheet. A3 printing uses the selected sheet and current layer visibility; printed scale is page-fit, not the original CAD scale.

Validation includes unchanged DWG/scene/SKP hashes, all source dimension entities, SVG parsing and source inventories, actual browser zoom/pan/layer/mode controls, mobile layout and synthetic pinch gestures. Physical phone testing is reported separately.

Exporter references: [Autodesk DXF API](https://help.autodesk.com/cloudhelp/2026/ENU/OARX-ManagedRefGuide/files/OARX-ManagedRefGuide-Autodesk_AutoCAD_DatabaseServices_Database_DxfOut_string_int_DwgVersion.html) and [ezdxf drawing documentation](https://ezdxf.readthedocs.io/en/stable/addons/drawing.html).
