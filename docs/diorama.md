# Revision 06: night diorama presentation

The existing public Ngoro viewer now opens with a cool navy miniature presentation, a raised base, warm windows and localized lighting, restrained wet-paving highlights, and fine rain. The visual reference was https://x.com/beefnoode/status/2107417865406324750. No source code or assets from that post were copied.

Use **Gaya visual → Arsitektur** to return to the original architectural materials and daylight. The Siang/Senja controls also return to architectural presentation. Changing visual styles exits walkthrough before restoring the appropriate orbit lens. Full-site views fit the complete base to the viewport; first/third-person navigation remains available.

The diorama adds eight draw objects, without a full-screen postprocessing or real-time reflection pass. Rain uses one line buffer and drops to 140 streaks on lightweight/adaptive-reduced quality. Reduced-motion preferences suppress rain. The paving highlights are stylized light pools, not physically traced reflections.

Model coordinates, source DWG, 12 vector drawing views, SketchUp download, collision/navigation module and door animation module are unchanged. The plinth and effects belong to a separate presentation group and do not enter CAD exports or collision geometry.

## Verification

Run `python scripts/verify_diorama.py`. This validates protected asset identities against revision 05, all 12 SVG sheets and manifest hashes, JavaScript syntax, reversible material changes, bounded additional geometry/rain, walking-camera switching and projection containment at desktop, square and portrait aspect ratios.

The original `scripts/verify_drawings.py` is the revision-05 historical verification script and intentionally asserts the exact revision-05 app code. It passed before this graphics change; use `verify_diorama.py` for revision 06. Historical browser test receipts are not reused as evidence for this revision.

Local headless Chromium could not start because the execution platform disallowed its IPC socket; the supported escalation returned the same failure. The cloud browser also rejected the attempted preview/navigation route. Static/unit checks do not establish browser/GPU rendering or physical-device performance.
