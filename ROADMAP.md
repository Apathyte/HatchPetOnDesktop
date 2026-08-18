# Dex v12 Roadmap

This roadmap starts a new planning line after the locked `stable-v11-walk-cleanup-backlog` baseline. It is intentionally additive: no deletes, no stable snapshot rewrites, and no changes to `main` until a branch has been reviewed.

## Working Name

`v12-project-continuity`

The point of v12 is not only new behavior. It also makes the repository self-contained enough for development to continue across clean environments without relying on private conversations or machine-specific context.

## Branch And Version Policy

- Use feature or planning branches for all non-trivial work.
- Keep `main` as the known-good line unless deliberately merging a reviewed version.
- Keep existing `stable-v*` folders untouched unless explicitly creating a new stable snapshot.
- Treat the next stable snapshot as `stable-v12-*` after the desktop overlay has a coherent improvement set, not after every tiny patch.
- Prefer small grouped updates: one branch for planning, one branch for menu/status polish, one branch for sprite redraw work, one branch for reaction behavior/art.
- No deletes unless explicitly called out and confirmed.

## Current Source Of Truth

- `README.md` describes stable versions v1 through v11 and the current backlog.
- `dex_desktop.py` is the real Windows desktop overlay.
- `index.html`, `styles.css`, and `dex.js` are the browser simulation/prototype.
- `run_dex.bat` is the double-click desktop launcher.

## Current Backlog From v11

- Clean up remaining sit-emote pixel artifacts.
- Redraw walking/patrol lower-body frames carefully rather than quick artifact removal.
- Make always-on-top state more visibly checked/unchecked in the right-click menu.
- Add dedicated sprites/reactions for Excel disappointment/growl, PowerPoint boredom, meeting fatigue, and engineering supervision.

## Singular Vision Questions

Answering these should happen before major v12 implementation. Short answers are fine.

1. Who is Dex at the personality level: calm guardian, grumpy shop dog, gentle supervisor, chaos detector, or some blend?
2. Should Dex feel mostly autonomous, or mostly like a controllable desktop toy with reactions layered on top?
3. What is the acceptable interruption level during work: subtle ambient companion, noticeable but rare, or playful and opinionated?
4. Should app reactions be practical status signals, character jokes, or both?
5. Which reactions are canon and worth dedicated art first: Excel, PowerPoint, Teams/Zoom, VSCode, terminal, Docker, Node-RED, Ignition, CPU spike, inactivity?
6. Should Dex ever make sound, or remain fully silent/visual?
7. Should he stay pixel-art only, or can some UI elements be cleaner desktop-native controls?
8. What should count as a release-quality stable version: visual polish, behavior polish, reliability, or a balanced bundle?
9. How much should the browser prototype matter now that the desktop overlay is running for real?
10. Should future work optimize for all-day use first, or richer character expression first?

## Initial Vision Decisions

These are the first v12 answers and should guide implementation unless later revised.

- Dex is a calm guardian first. Specific emotes should appear through context and deliberate reactions, but his base identity is protective and steady.
- Dex should be autonomous. Manual and test controls exist mainly to confirm how autonomous behavior will work, not because the final experience should depend on constant user commands.
- Dex can be playful and opinionated for now. The exact interruption level should be revisited after more real all-day use.
- Initial reaction priority is: Excel, PowerPoint, Terminal, CPU spike, Inactivity. Other reactions can follow later based on usefulness or charm.
- The current reliability floor is already good enough for a stable baseline. v12 should focus more on movement quality, sprite cleanup, and reducing visible jank/blobbage.
- Expression should mostly use balloons/overlays for now because dedicated facial/body emotes are currently where sprite blobbage appears most easily. The tongue/emote attempts are a warning sign: do not force too much expression into the base sprite until the animation art pipeline is healthier.

## v12 Candidate Work Packages

### 1. Planning And Memory

Goal: make the repo carry the project context across machines.

- Add this roadmap.
- Add a brief decision log once answers to the singular vision questions are known.
- Keep durable technical decisions in the repository instead of relying on external conversations.

### 2. Desktop Reliability And Controls

Goal: preserve the already-acceptable all-day desktop baseline.

- Improve right-click menu state indicators when convenient, but do not let control polish distract from the movement/sprite work.
- Confirm pause, always-on-top, status window, and exit flows behave consistently.
- Add a lightweight diagnostics note for foreground app detection and CPU readings only if it helps future debugging.
- Avoid adding dependencies unless they clearly improve the Windows desktop experience.

### 3. Reaction System

Goal: make reactions feel intentional while avoiding fragile sprite-emote work too early.

- Define a small reaction profile table for app, trigger, pose, overlay, text/bubble, duration, and priority.
- Keep manual test reactions available from the right-click menu.
- Prioritize balloons/overlays for v12 expression.
- Add dedicated body/facial sprites only after the movement and sprite pipeline are less janky.

### 4. Sprite And Motion Cleanup

Goal: make Dex feel comfortable living on the desktop all day, not just acceptable as a prototype.

- Preserve the current v11 baseline before any redraw work.
- Work on walking/patrol lower-body frames in a separate branch.
- Prefer before/after screenshots or sprite contact sheets for review.
- Do not quick-fix stray pixels if the real issue is frame anatomy.
- Treat general movement quality and visible blobbage as the main v12 stable target.

### 5. Continuity Validation Pass

Goal: reconcile this plan with any relevant external technical notes before promotion.

Future check:

- Summarize only the non-sensitive technical decisions needed by the project.
- Compare those decisions against this roadmap.
- Mark any missing intent, rejected ideas, personality decisions, or next-step commitments.
- Update the roadmap or decision log before starting larger v12 implementation.

This check is expected to refine the next steps, not block small safe improvements.

## Animation Strategy

Current recommendation: keep iterating this way for v12, but define a future promotion point.

### v12: Clean The Current System

- Stay with the current Tkinter desktop overlay and existing sprite-frame assets.
- Improve the walk/patrol frames enough that Dex feels less janky in daily use.
- Keep expression mostly in balloons and overlays.
- Add tooling only if it helps review the sprite frames, such as a contact sheet or before/after preview.

### Future v13 Or Later: Promote The Animation Pipeline

Move up when frame-by-frame cleanup stops producing good returns. Candidate direction:

- Separate behavior state, animation timing, sprite assets, and overlays more cleanly.
- Use explicit animation definitions instead of hardcoded pose/frame choices spread through the desktop runtime.
- Consider a proper sprite-sheet/metadata workflow for frame timing, anchors, contact points, and overlays.
- Keep Tkinter if it remains enough for the desktop overlay, but make the animation system less dependent on one-off code tweaks.

Promotion trigger: if walking, sitting, or app-specific emotes keep requiring fragile pixel fixes or create new blobbage, stop adding emotes and refactor the animation pipeline first.

## v12 Balance Question

The reliability-versus-expression answer is now:

- Reliability floor: the current desktop baseline is already above the minimum expected stable standard.
- v12 stable target: reduce janky movement and sprite blobbage enough that Dex feels natural to leave running on the desktop.
- Expression ceiling: use opinionated balloons/overlays for contextual emotes while avoiding complex base-sprite expression until the art/animation pipeline improves.
- Release bundle: movement cleanup plus balloon-driven Excel/PPT/Terminal/CPU/Inactivity reactions is enough to justify a `stable-v12-*` candidate.

## Preload Requirements For Future Sessions

Useful things to have ready before implementing v12 work:

- A clean checkout of the repository.
- Confirmation of which branch should be edited.
- A current screenshot or quick description of what looks wrong when Dex is running.
- A sanitized summary of any external technical decisions needed for the validation pass.
- Whether changes should be local-only, committed to a branch, or opened as a PR.
- Python available on Windows for `run_dex.bat`; Tkinter is expected from the standard Python install.
- For sprite work, the relevant `assets/dex-concept` frames and a preferred review method: screenshots, contact sheet, or live run.

## First Recommended v12 Move

Start with a movement/sprite review branch:

- Generate or inspect a frame contact sheet for the current walk/patrol/sit frames.
- Identify whether the blobbage is mostly in source PNG frames, runtime placement/anchor issues, or motion timing.
- Make the smallest cleanup that improves daily movement quality without changing Dex's core silhouette.

Then add balloon-driven reaction profiles for Excel, PowerPoint, Terminal, CPU spike, and Inactivity.
