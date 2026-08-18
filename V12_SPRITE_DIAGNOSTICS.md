# Dex v12 Sprite Diagnostics

This note captures the pre-promotion sprite review after the reaction-state pass. No sprite PNGs are edited in this pass.

## User-Visible Issues

- Sitting pose still has visible white cleanup pixels.
- Patrol and walking/trot frames still show black blobbage underneath the body around the legs.
- One behind leg in patrol does not read as animated like the other paws.
- Patrol has visible white pixels near the ear and above the eye.
- A small black blob appears for a single frame outside the sprite on the right side of the body across multiple animations.

## Diagnostic Artifacts

- `assets/previews/v12-sprite-defect-diagnostics-contact-sheet.png`
- `assets/previews/v12-sprite-defect-diagnostics-contact-sheet.txt`
- Existing before/after cleanup reference: `assets/previews/v12-trot-artifact-cleanup-contact-sheet.png`

The diagnostic sheet intentionally focuses on head crops, lower-body crops, and right-edge crops. Red overlay marks opaque near-white pixels in reviewed head crops so the remaining cleanup pixels can be validated visually.

## Read

The remaining defects are no longer just a simple transparent-background cleanup problem.

- The lower-body blobbage and stiff behind leg point at source-frame and animation-cycle limits.
- The right-edge one-frame blob should be treated as an edge-frame artifact until it is caught live or isolated in a frame diff.
- The white pixels can still be cleaned surgically, but that will not fix the leg-cycle problem.

## Recommendation Before Promotion

Promote the reaction-state fix separately from broad sprite redraw work if the live behavior is stable.

Keep the sprite issues as a known v12 visual limitation unless the next pass is explicitly a targeted pixel cleanup pass. The healthier route is to prep the v13 animation pipeline spike before investing heavily in manual sprite patching, because the user's desired Pack 1 emotes need reusable beats, anchors, frame timing, and transitions.

## Next Visual Pass

1. Use the diagnostic sheet to confirm which visible white pixels are acceptable versus must-fix.
2. If doing v12 cleanup, edit only the specific sitting/head white pixels and obvious right-edge artifact frames.
3. Do not attempt to solve the behind-leg animation by pixel cleanup alone.
4. For patrol/trot, evaluate whether frame timing, foot contact anchors, or a new generated frame set is the real fix.
5. Feed confirmed defects into the v13 animation metadata spike.
