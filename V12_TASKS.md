# Dex v12 Task List

This file separates v12 work into reviewable tasks that can be run autonomously while keeping Dex's stable baseline safe.

## Autonomy Rules

Codex may do these without stopping for approval:

- Read repo files, inspect branches, and summarize findings.
- Create new feature/planning branches from the current reviewed branch.
- Add new docs, notes, diagnostics, contact sheets, or preview helpers.
- Make small scoped code changes on a feature branch when the task has a clear acceptance test.
- Commit changes to feature branches with descriptive messages.

Codex should ask first before doing these:

- Editing `main` directly.
- Creating or replacing a `stable-v*` snapshot.
- Deleting files, assets, branches, or old versions.
- Reworking Dex's core silhouette or personality direction.
- Adding new runtime dependencies.
- Merging branches or opening a PR if that changes the intended review flow.

Explicit defaults:

- No deletes.
- No `main` edits.
- Stable folders are read-only unless told otherwise.
- Prefer branches grouped by task lane.
- Keep repo memory in Markdown files so laptop switching is painless.

## Task Lanes

### Lane 0: Planning And Memory

Purpose: keep the project understandable across machines and chat threads.

Tasks:

- Keep `ROADMAP.md` current as vision decisions land.
- Keep this task list current as work is split or completed.
- Add a `DECISIONS.md` file if the roadmap starts getting too dense.
- Later, run the work-laptop chat validation pass and update roadmap/tasks from that context.

Review checkpoint:

- User confirms the task lanes and autonomy rules are acceptable.

### Lane 1: Movement And Sprite Audit

Purpose: find the real source of janky movement and blobbage before touching art.

Branch suggestion: `audit/v12-movement-sprite`

Tasks:

- Inventory current sprite assets, especially walk/trot, patrol, sit, sleep, happy, leash, and zoom frames.
- Generate or add a contact-sheet helper for current frames.
- Compare right-facing and left-facing frames for mismatched pixels, offsets, or artifacts.
- Check runtime placement constants such as sprite Y position, stride offset, frame rate, and direction handling.
- Produce an audit note with findings grouped as source-frame issue, anchor/placement issue, timing issue, or behavior issue.

Acceptance output:

- A contact sheet or equivalent visual review artifact.
- A short written audit saying where the blobbage most likely comes from.
- No sprite cleanup yet unless the cause is trivial and isolated.

Autonomous allowed:

- Yes, safe to run fully autonomous.

### Lane 2: Minimal Movement Cleanup

Purpose: improve daily movement without refactoring the whole animation system.

Branch suggestion: `feature/v12-movement-cleanup`

Tasks:

- Use Lane 1 findings to pick the smallest high-impact movement fix.
- Prefer anchor/timing/placement improvements before pixel redraw if that fixes visible jank.
- If source PNG cleanup is needed, edit only the smallest set of frames.
- Preserve Dex's current silhouette and calm guardian feel.
- Keep before/after review material.

Acceptance output:

- Movement looks less janky in live desktop use or contact-sheet comparison.
- No new visible sprite artifacts.
- No personality or silhouette drift.

Autonomous allowed:

- Partially. Codex can implement anchor/timing/code fixes autonomously. Pixel-art redraws should pause for review after the audit unless the change is tiny artifact cleanup.

### Lane 3: Balloon-Driven Reaction Profiles

Purpose: add expression without forcing fragile facial/body emotes into the base sprite.

Branch suggestion: `feature/v12-reaction-profiles`

Priority order:

1. Excel
2. PowerPoint
3. Terminal
4. CPU spike
5. Inactivity

Tasks:

- Define reaction profiles with trigger, priority, pose, balloon text, duration, cooldown, and test-menu entry.
- Keep balloons short and opinionated.
- Make manual test controls continue to simulate reactions.
- Avoid dedicated base-sprite emotes in v12 unless movement cleanup makes the pipeline healthier.

Acceptance output:

- Each priority reaction can be manually tested.
- Reactions are visible but not constant spam.
- Dex remains guardian-first, not pure novelty.

Autonomous allowed:

- Yes for code and balloon copy drafts. User review is useful for final wording/tone.

### Lane 4: Desktop Control Polish

Purpose: keep existing reliability above the stable floor.

Branch suggestion: `feature/v12-control-polish`

Tasks:

- Improve always-on-top menu state display if it is quick.
- Confirm pause/resume label behavior.
- Confirm status window stays readable and topmost state is consistent.
- Avoid making this lane larger than needed.

Acceptance output:

- Existing controls feel clear enough for all-day use.
- No new dependency or UI complexity.

Autonomous allowed:

- Yes.

### Lane 5: Future Animation Pipeline Spike

Purpose: clarify when to stop patching frames and move up to a healthier animation system.

Branch suggestion: `spike/v13-animation-pipeline`

Tasks:

- Draft an animation metadata shape for pose, frames, facing direction, anchor point, contact point, frame rate, overlays, and movement speed.
- Identify what would change in `dex_desktop.py` if animation definitions were data-driven.
- Do not replace the runtime in v12.

Acceptance output:

- A short proposal that helps decide whether v13 should refactor animation handling.

Autonomous allowed:

- Yes for a document/spike. No runtime rewrite without user confirmation.

### Lane 6: Real-Clock Break Reminder

Purpose: make Dex bring his leash on a real hourly cadence, not only as a passive inactivity side effect.

Branch suggestion: `feature/v12-clock-reminder`

Tasks:

- Add a small reminder class that tracks wall-clock reminder cadence.
- Let the reminder trigger Dex's leash mode when the hourly break is due.
- Keep it app-internal first so it works while Dex is running.
- Defer Windows scheduled task integration unless reminders are needed while Dex is not running.
- Add menu/test visibility so the behavior can be validated without waiting a full hour.

Acceptance output:

- Dex can enter leash mode from a real-clock reminder.
- Reminder behavior is configurable or easy to disable.
- No external scheduler is required for the first version.

Autonomous allowed:

- Yes for a scoped app-internal reminder class. Ask before adding Windows scheduled task setup.

## Recommended Run Order

1. Lane 0: confirm task separation and autonomy rules.
2. Lane 1: audit movement and sprites.
3. Lane 2: make one minimal movement cleanup pass.
4. Lane 3: implement balloon-driven reactions in priority order.
5. Lane 4: polish controls if quick or if bugs appear during testing.
6. Lane 5: document the future animation-pipeline promotion path.
7. Lane 6: add a real-clock leash reminder class when the reaction/movement baseline is accepted.

## First Autonomous Run Proposal

Start with Lane 1 only:

- Create `audit/v12-movement-sprite` from `roadmap/v12-cross-laptop-vision` or from the selected base branch.
- Inspect sprite assets and runtime animation code.
- Add a contact-sheet helper or generated review artifact if useful.
- Produce an audit note.
- Stop before broad sprite edits.

This gives the next implementation step better evidence instead of guessing at the blobbage.
