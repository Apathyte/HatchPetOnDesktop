> Public note: this is a personal hobby prototype inspired by the desktop pet / Hatch Pet idea. It is not an official Hatch Pet package, not a polished application, and not affiliated with any workplace or vendor project.
> 
# Dex Desktop Pet


Dex is a static browser prototype and Windows desktop overlay trial for a pixel-art workstation companion: a stocky charcoal-black Cane Corso and pit bull mix with an old grey muzzle, calm protector energy, and grumpy workstation personality.

`stable-v1/` contains the first stable desktop trial.
`stable-v2/` contains the improved hand-drawn Tkinter version.
`stable-v3/` contains the liked concept-sprite version before grounded-motion experiments.
`stable-v4-halfway-walk/` contains the first acceptable leg-motion halfway state.
`stable-v5-anchored-walk/` contains the current stable anchored walk, with behind-leg motion still noted for a future pass.
`stable-v6-functional-baseline/` contains the locked desktop-functionality baseline for behavior and menu iterations.
`stable-v7-functional-awareness/` contains the first stable app-aware desktop version with expanded right-click commands.
`stable-v8-live-diagnostics/` contains the app-aware version with live-updating status diagnostics.
`stable-v9-corso-clean/` contains the cleaned Corso-proportion trial with artifact-cleaned sprite edges.
`stable-v10-growl-balloon-clean/` contains the confirmed Excel growl balloon version with cleaned detached sit-sprite artifacts.
`stable-v11-walk-cleanup-backlog/` contains the current working desktop version with growl balloon, detached artifact cleanup, and remaining walking lower-body redraw work documented.
`v12-reaction-state-and-sprite-diagnostics` brings the current main branch up to the reaction-profile baseline: contextual reaction profiles, manual test reactions, status diagnostics, sprite cleanup tooling, and placeholder emote behavior before final sprite redraws.

Open `index.html` in a browser to try it. Dex is rendered on canvas, so his sprite and behavior states are generated live rather than stored as fixed image frames.

## Current Behaviors

- Slowly trots around the simulated desktop.
- Sits, lays down, sleeps, patrols, paces, and drops a leash.
- Right-click menu supports attention, walking, zoomies, nap, wake, patrol, leash, sit/stay, resume, reset, always-on-top, pause, and exit.
- Right-click menu includes `Show status` for current mode, pose, detected app, reaction, CPU, and always-on-top state.
- Right-click menu includes `Test reactions` for manually simulating Excel, PowerPoint, meeting fatigue, and engineering supervision.
- Excel reaction shows a small `GRROWWLL` balloon above Dex without modifying the base sprite art.
- The always-on-top menu item shows `yes` or `no`.
- Desktop overlay detects the foreground Windows app/window title read-only.
- Reacts to spreadsheets, presentations, code editors, terminals, meetings, heavier runtime contexts, and CPU spikes.
- Gets more persistent after long inactivity.
- Can be dragged around the screen as a short walk.
- Can enter midnight patrol and has rare zoomies.
- Uses v12 reaction profiles with priorities, durations, cooldowns, test-menu entries, and placeholder bubbles/overlays.

## Files

- `index.html` - desktop simulation and controls.
- `styles.css` - retro workstation UI and responsive layout.
- `dex.js` - canvas sprite renderer, animation states, and behavior profile.
- `dex_desktop.py` - dependency-free Windows desktop overlay trial.
- `run_dex.bat` - double-click launcher for the desktop overlay.

## Desktop Trial

Double-click `run_dex.bat` to let Dex run around on the actual desktop. Left-drag him to walk him. Right-click Dex for attention, zoomies, or exit.

## Nice-to-Haves

- Revisit sit-emote pixel cleanup; small white pixelation remains and is intentionally deferred.
- Revisit walking/patrol sprite cleanup; some remaining lower-body blobbage is part of the drawn sprite frames and needs a careful redraw pass rather than quick artifact removal.
- Bug/CR: Excel growl reaction should clear automatically when Excel is closed or loses foreground focus, ideally as soon as the user clicks into a different window.
- Future use case: hourly walk reminder. Dex should validate roughly 60 minutes of seated/inactive time, grab or drop his leash, and ask to be walked. Runtime scheduling and final leash animation can be implemented separately; a placeholder emote is acceptable while graphics are refined.
- Add a visible checked/unchecked indication for `Toggle always on top`, such as an on/off label or checkmark in the right-click menu.
- Add dedicated sprites for Excel disappointment/growl, PowerPoint boredom, meeting fatigue, and engineering supervision.

For all-day use, put a shortcut to `run_dex.bat` in the Windows Startup folder:

```text
Win + R -> shell:startup
```

Then paste a shortcut there.
