# Dex v12 Reaction Spec Validation

Branch: `feature/v12-reaction-profiles`

Purpose: make the v12 emote/reaction plan visible before implementation continues. This separates what the specs require, what already exists, and what is only a placeholder/draft.

## Spec Summary

From `ROADMAP.md` and `V12_TASKS.md`, v12 reactions should:

- Keep Dex as a calm guardian first.
- Use contextual, deliberate reactions rather than constant novelty.
- Stay autonomous; manual/test controls are validation tools.
- Use balloons/overlays for v12 expression.
- Avoid dedicated facial/body sprite emotes until the movement/sprite pipeline is healthier.
- Support priority reactions in this order: Excel, PowerPoint, Terminal, CPU spike, Inactivity.
- Define profiles with trigger, priority, pose, overlay/text bubble, duration, cooldown, and test-menu entry.
- Keep each priority reaction manually testable.
- Avoid reaction spam.

## Current Implementation State

| Reaction | Spec Intent | Current Trigger | Current Pose | Current Bubble/Overlay | Test Menu | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Excel | First-priority opinionated growl/disappointment | `excel.exe` foreground | `sit` | `GRROWWLL` balloon | Yes | Implemented |
| PowerPoint | Bored/opinionated reaction | `powerpnt.exe`; long active time sleeps | `sit` or `sleep` | `SIGH.` or `YAAWN...` | Yes | Implemented |
| Terminal | Guardian/supervision reaction for terminal work | Terminal executables | `patrol` | `ON WATCH` | Yes | Implemented |
| CPU spike | Alert/protective reaction | CPU >= 85 percent | `patrol` at 1.4x movement speed | None by design | Yes | Implemented placeholder emote |
| Inactivity | Persistent guardian asks for a walk | Manual test profile; legacy long inactivity remains passive | `leash`, item `leash` | `WALK?` in test profile | Yes | Testable placeholder; real clock reminder deferred |
| Meeting | Existing non-priority reaction | Teams/Zoom foreground | `sit` or `leash` | None in committed behavior | Yes | Existing secondary behavior |
| Engineering supervision | Existing non-priority reaction | VSCode, terminals, Docker, Node-RED/Ignition title tokens | `patrol` | None in committed behavior | Yes | Existing broad behavior |

## Profile State

`REACTION_PROFILES` is now wired into:

- `build_test_reaction_menu`
- `apply_named_reaction`
- `draw_reaction_overlays`

`apply_activity_reaction` still owns trigger order and maps foreground app/CPU conditions to reaction names.

Current placeholder copy:

| Reaction | Draft Bubble | Needs User Eye? |
| --- | --- | --- |
| Excel | `GRROWWLL` | Low; already accepted baseline |
| PowerPoint | `SIGH.` / `YAAWN...` | Placeholder until real bored/yawn animation |
| Terminal | `ON WATCH` | Approved as placeholder; should become more Dex-like in animation pass |
| CPU spike | No balloon; 1.4x patrol speed | Placeholder until real alert animation |
| Inactivity | `WALK?` in test profile | Placeholder until real leash/reminder animation |
| Meeting | `STILL?` / `WALK.` | Pack 2 |
| Engineering supervision | `STEADY.` | Pack 2 |

## What Is Placeholder For Review

These items are placeholders, not final emotional design:

- Terminal should eventually feel more Dex-like than plain `ON WATCH`, but the placeholder is accepted for now.
- CPU spike should eventually be less literal than a text label; current placeholder is faster patrol movement.
- Inactivity should eventually be a real leash/reminder animation rather than relying on text.
- PowerPoint should become an emotional progression: boredom, sigh/yawn, then nap.
- Meeting and engineering reactions should stay as the second pack of emotes.

## Accepted Design Decisions

- Keep the earlier PowerPoint spec: PowerPoint makes Dex bored/sitting first, then sleep after a longer active duration. Do not switch to immediate sleep.
- PowerPoint yawn transition can be balloon-based before the sleep sprite because v12 expression should avoid fragile base-sprite emotes.
- Eventually PowerPoint should become a small emotional animation sequence rather than just one pose or one balloon.
- Terminal `ON WATCH` is approved as a placeholder.
- CPU spike speed behavior is implementation-choice; prefer movement-speed change first, not faster frame cycling, to avoid amplifying leg jank.
- Inactivity can stay implementation-choice for now. Long-term goal is for Dex to bring his leash roughly every hour as a real break reminder.
- Meeting and engineering reactions should be treated as the second emote pack.

## Inactivity / Leash Design Notes

End goal: Dex should periodically remind the user to get up and walk away, effectively by coming with his leash.

Open design issue:

- App-internal timer is simpler and keeps behavior inside Dex.
- OS-level scheduled task/cron-style reminder is more explicit, but heavier and less portable across machines.
- A hybrid may be best later: Dex tracks inactivity internally, but can optionally expose a separate hourly reminder mode.

Current v12 recommendation:

- Keep leash as the canonical long-inactivity reminder.
- Do not replace leash with sleep as the end-state.
- For now, make inactivity testable rather than solving the full clock/reminder architecture.
- Later nice-to-have: add a separate real-clock reminder class that can trigger leash mode roughly every hour.
- Possible later integration: the reminder class can stay app-internal first, then optionally connect to a Windows scheduled task helper if Dex needs reminders even when not already running.

## Implemented In `feature/v12-reaction-profiles`

- Reaction profiles are wired into manual test menu generation.
- Excel keeps `GRROWWLL` while using the generic balloon drawing path.
- PowerPoint keeps the earlier behavior: bored/sitting first, then sleep after longer active duration.
- PowerPoint long-duration sleep uses a `YAAWN...` balloon as the placeholder transition.
- Terminal has a distinct `terminal_watch` reaction with approved `ON WATCH` balloon.
- CPU spike keeps patrol pose and receives a 40 percent movement-speed multiplier without a balloon.
- Inactivity has a profile/test entry for leash mode, while the existing passive long-inactivity behavior remains in place.
- The real-clock hourly leash reminder is backlog as a separate class/lane, not implemented in this branch.

## Remaining Implementation Gap

The code does not yet have:

- Per-reaction duration.
- Per-reaction cooldown.
- Real-clock hourly leash reminder.
- Dedicated status display of profile metadata beyond the current reaction name.
- Animation/emote specs for the final non-placeholder reactions.

## Emote Pack Plan

Detailed animation intent now lives in `V12_EMOTE_SPEC.md`.

### Pack 1: Current v12 Placeholders

- Excel: growl/disappointment.
- PowerPoint: bored, sigh/yawn, eventual nap.
- Terminal: guardian watch.
- CPU spike: alert patrol.
- Inactivity: leash/reminder.

### Pack 2: Later Secondary Emotes

- Meeting fatigue.
- Engineering supervision.
- Docker/Node-RED/Ignition-specific variants if they prove useful.

### Animation Prep

Before replacing placeholders with real emotes, define:

- Trigger and priority.
- Emotional arc, not just final pose.
- Start pose, transition pose, and end pose.
- Whether the animation should move Dex, change only overlays, or use a dedicated sprite cycle.
- Duration and cooldown.
- What should happen if a higher-priority reaction interrupts it.

## Recommended Next Implementation

After maintainer review:

1. Validate live behavior through the right-click test menu.
2. Decide whether the stacked movement + reaction branch should become a v12 candidate.
3. Add simple anti-spam timing only after the base profile behavior is visible and accepted.
4. Implement the real-clock leash reminder in a separate lane/branch.
5. Start the animation/emote spec before trying more sprite edits.
