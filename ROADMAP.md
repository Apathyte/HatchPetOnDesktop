# Dex v12 Roadmap

This roadmap starts a new planning line after the locked `stable-v11-walk-cleanup-backlog` baseline. It is intentionally additive: no deletes, no stable snapshot rewrites, and no changes to `main` until a branch has been reviewed.

## Working Name

`v12-cross-laptop-vision`

The point of v12 is not only new behavior. It is also the first version planned with the expectation that work may alternate between a personal PC and a work laptop. The repo should carry enough memory that the project does not depend on any one chat thread.

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
- The all-day reliability versus richer expression question needs another level of detail. It is expected to be a mix, not a strict either-or.

## v12 Candidate Work Packages

### 1. Planning And Memory

Goal: make the repo carry the project context across machines.

- Add this roadmap.
- Add a brief decision log once answers to the singular vision questions are known.
- Keep branch notes in the repo instead of relying only on chat history.

### 2. Desktop Reliability And Controls

Goal: make Dex more comfortable for all-day desktop use.

- Improve right-click menu state indicators.
- Confirm pause, always-on-top, status window, and exit flows behave consistently.
- Add a lightweight diagnostics note for foreground app detection and CPU readings.
- Avoid adding dependencies unless they clearly improve the Windows desktop experience.

### 3. Reaction System

Goal: make reactions feel intentional rather than just pose switches.

- Define a small reaction profile table for app, trigger, pose, overlay, text/bubble, duration, and priority.
- Keep manual test reactions available from the right-click menu.
- Add dedicated overlays or sprites in priority order after the vision answers land.

### 4. Sprite And Motion Cleanup

Goal: improve the walk without losing Dex's current liked look.

- Preserve the current v11 baseline before any redraw work.
- Work on walking/patrol lower-body frames in a separate branch.
- Prefer before/after screenshots or sprite contact sheets for review.
- Do not quick-fix stray pixels if the real issue is frame anatomy.

### 5. Cross-Laptop Validation Pass

Goal: reconcile this plan with context from the work laptop.

Future check:

- Export, paste, or summarize the relevant work-laptop chat history.
- Compare that context against this roadmap.
- Mark any missing intent, rejected ideas, personality decisions, or next-step commitments.
- Update the roadmap or decision log before starting larger v12 implementation.

This check is expected to refine the next steps, not block small safe improvements.

## v12 Balance Question

The remaining planning question is how to balance all-day comfort with richer character expression. Suggested framing:

- Reliability floor: the things Dex must do before any expressive feature counts as shippable. Examples: no annoying focus stealing, stable exit/pause controls, predictable topmost behavior, readable status, no runaway CPU.
- Expression ceiling: the richest behavior Dex should have in v12 without becoming distracting. Examples: dedicated Excel/PPT/terminal emotes, short opinionated bubbles, calmer idle guarding, rare bigger reactions.
- Release bundle: the smallest mix of both that deserves `stable-v12-*`.

Open follow-up: what is the minimum reliability floor, and what is the most important expression ceiling for v12?

## Preload Requirements For Future Sessions

Useful things to have ready before asking Codex to implement v12 work:

- The local path to the checked-out repo on the machine being used.
- Confirmation of which branch should be edited.
- A current screenshot or quick description of what looks wrong when Dex is running.
- Any work-laptop chat export, pasted excerpts, or summary for the validation pass.
- Whether changes should be local-only, committed to a branch, or opened as a PR.
- Python available on Windows for `run_dex.bat`; Tkinter is expected from the standard Python install.
- For sprite work, the relevant `assets/dex-concept` frames and a preferred review method: screenshots, contact sheet, or live run.

## First Recommended v12 Move

Start with a low-risk branch for desktop control polish:

- Better checked/unchecked right-click menu state for always-on-top.
- Confirm pause/resume label behavior.
- Add or update a short decision log after the vision questions are answered.

Then move into reaction profiles and sprite redraw work once the singular vision is settled.
