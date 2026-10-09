# Ngoro construction playback

Open the current viewer with `?mode=construction`, or select **Gaya visual → Tahap konstruksi**. The earlier **Diorama malam** and **Arsitektur** modes remain available. Plain URLs keep the earlier default presentation.

The reference was the actual construction-sequence video in https://x.com/irinatoxi/status/2108207321423769816. Its pale technical presentation, staged reveal, timeline and counters informed this adaptation. Its hangar geometry, tonnage, bolt count, crane specification and 24-week schedule are not Ngoro data and were not imported.

## What the sequence means

Eight illustrative phases classify the existing 9,972 source-model elements: site preparation; foundations and tie beams; columns and anchors; framing and bracing; walls and roofs; floors and access; interiors and utilities; landscaping and completion. The classifications use source groups and element names. They are a presentation sequence, not a verified erection method, structural analysis, construction schedule, bill of quantities or progress-weight calculation.

Play advances one phase every five seconds. The slider, phase buttons and previous/next controls allow immediate inspection. Scrubbing pauses playback. Playback stops at the last phase; pressing Play again restarts. Switching away, opening drawings or hiding the page pauses playback.

Soil is temporarily hidden during phases 2–5 so below-grade foundations remain readable. This is a visibility cutaway: source coordinates and geometry are unchanged. Counts refer to unique model elements displayed, including obscured geometry, not actual installed items or tonnage. The ground/grid is presentation context.

The current phase is tinted blue. Doors and walkthrough pause while this mode is active; their existing state, model matrices, materials, instance colours and parent visibility are restored on exit. Orbit and preset views remain usable. Original CAD/SKP/DWG downloads and all 12 vector sheets are unchanged.

## Verification and limits

Run `python scripts/verify_diorama.py` for the protected-asset and original-mode checks, then `node --test scripts/test-construction.mjs` and `node --check web/dist/construction.js`. New tests cover classification of all existing elements, reversible matrices/materials/colours, merged meshes, paused/restarted/completed playback, UI controls and the temporary soil cutaway.

Actual reference pixels were inspected at the beginning, frame/connection detail and late assembly stages. The current cloud browser reports `GL_VENDOR = Disabled` and cannot create WebGL, so a live WebGL screenshot, GPU behavior and physical-device performance cannot be certified here. A separate Blender CPU render can check source-derived foundation/frame composition, but is not a screenshot of this web renderer or proof of its performance.
