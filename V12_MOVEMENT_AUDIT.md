# Dex v12 Movement And Sprite Audit

Branch: `audit/v12-movement-sprite`

This audit checks why Dex's current desktop movement still feels janky and why sprite expression tends to turn into blobbage. It is intentionally diagnostic: no sprite redraws and no runtime behavior changes yet.

## Current Runtime

- `dex_desktop.py` loads active frames from `assets/dex-concept`.
- Active walking-style poses are four-frame cycles: `trot`, `happy`, `patrol`, and `zoom`.
- Static/near-static poses are single-frame pairs: `sit`, `sleep`, and `leash`.
- Runtime sprite placement is fixed at `SPRITE_Y = PET_H - 132 + 2`.
- Runtime frame drawing adds `sprite_x = 2 + stride`, where `stride` flips between `-1` and `1` for moving poses.
- Runtime movement also uses `grounded_stride`, which alternates between a slow planted phase and a faster moving phase.

## Existing Review Artifacts

Useful existing previews:

- `assets/previews/trot-lower-body-contact-sheet.png`
- `assets/previews/trot-lower-body-contact-sheet-cleaned.png`
- `assets/previews/trot-lower-body-contact-sheet-after.png`
- `assets/previews/active-vs-v9-visual-compare.png`
- `assets/previews/*-alpha-flicker.png`

These already provide enough evidence for the first audit pass. The lower-body contact sheets show the walk issue clearly: the legs and paws have readable motion, but there are leftover detached tail/edge pixels and pale lower-body artifacts that travel through the frames.

## Findings

### 1. Source PNG Frames Are The Main Blobbage Source

The active `assets/dex-concept` frames already contain most of the lower-body artifacts before runtime movement is applied. This is supported by the existing contact sheets and the number of historical cleanup tools focused on white gaps, leg voids, tongue shape, and artifact cleanup.

Relevant tools/history:

- `tools/v3_leg_walk_cycle.py`
- `tools/derive_walk_frames.py`
- `tools/hybrid_v3_walk_frames.py`
- `tools/fill_between_leg_void.py`
- `tools/fix_between_leg_whites.py`
- `tools/kill_leg_gap_white.py`
- `tools/subtle_gap_cleanup.py`
- `tools/fix_tongue_shape.py`
- `tools/clean_sprite_artifacts.py`

This pattern suggests the previous iterations were fighting sprite anatomy and generated-frame artifacts, not just one bad pixel pass.

### 2. Runtime Timing Adds A Little Extra Jank

Runtime movement is not the primary source of blobbage, but it probably makes it more noticeable:

- The animation frame index runs by wall-clock time.
- `grounded_stride` also runs by wall-clock time.
- `draw_sprite_frame` adds a separate `-1/+1` horizontal sprite nudge based on `step_phase`.

Because the frame cycle, planted phase, and horizontal nudge are loosely related rather than defined as one animation, the body can feel like it is sliding or twitching on top of imperfect source frames.

### 3. Anchor/Contact Points Are Implicit

The current system has no per-frame anchor/contact metadata. Every frame is drawn at the same `SPRITE_Y`, with only the small runtime `sprite_x` stride offset. That means foot contact and body weight are implied by the PNGs themselves. If the PNG frame shifts, exposes a gap, or changes leg mass, the runtime has no way to compensate cleanly.

### 4. Expression Should Stay In Balloons For v12

The tongue/emote cleanup history confirms the current roadmap choice: do not push much expression into the base sprite yet. At this scale, small face/mouth edits become visual blobs quickly. Balloons and overlays are the safer v12 expression layer.

## Classification

| Issue | Primary Type | Notes |
| --- | --- | --- |
| Lower-body blobbage | Source-frame issue | Visible in contact sheets before runtime animation. |
| Detached edge/tail pixels | Source-frame issue | Contact sheets show small detached artifacts around rear/tail area. |
| Walk sliding/twitch | Timing/anchor issue | Runtime frame timing and stride nudge are not driven by explicit animation metadata. |
| Foot-ground consistency | Anchor/contact issue | No per-frame contact point exists. |
| Tongue/emote blobbage | Source-frame/detail-scale issue | Keep expression in balloons/overlays for now. |

## Recommended v12 Path

### First Cleanup Pass

Do not redraw the whole dog yet. Make one small movement-focused cleanup branch:

1. Remove or tone down the remaining detached tail/edge pixels visible in the current trot contact sheet.
2. Test whether disabling or reducing the runtime `sprite_x` stride nudge makes the walk calmer.
3. Keep `grounded_stride`, but consider making frame index derive from the same phase later.
4. Preserve the current silhouette and guardian feel.

### What Not To Do Yet

- Do not add dedicated facial/body emote sprites for Excel/PPT/terminal yet.
- Do not regenerate all sprites from scratch without a clearer art pipeline.
- Do not keep stacking cleanup scripts if each pass creates new artifact cleanup work.

## Future Pipeline Trigger

If one small v12 cleanup pass does not noticeably improve daily movement, promote the animation work before more art fixes:

- Define animation metadata for frame timing, anchor point, contact point, pose speed, facing direction, and overlays.
- Make animation frame selection and movement phase come from one shared animation state.
- Use contact sheets or a preview harness as part of every sprite change.

## Current Recommendation

Proceed to Lane 2 with a tiny, reversible movement cleanup:

- Try runtime calm-down first: reduce/remove the extra `sprite_x` nudge and compare feel.
- Then, if needed, do a very narrow source-frame cleanup of the remaining detached artifacts.
- Keep balloon-driven expression work separate from base-sprite cleanup.
