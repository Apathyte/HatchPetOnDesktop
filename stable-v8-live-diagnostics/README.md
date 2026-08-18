# Dex Desktop Pet

Dex is a static browser prototype for a pixel-art workstation companion: a stocky charcoal-black Cane Corso and pit bull mix with an old grey muzzle, calm protector energy, and engineering-shop personality.

`stable-v1/` contains the first stable desktop trial.
`stable-v2/` contains the improved hand-drawn Tkinter version.
`stable-v3/` contains the liked concept-sprite version before grounded-motion experiments.
`stable-v4-halfway-walk/` contains the first acceptable leg-motion halfway state.
`stable-v5-anchored-walk/` contains the current stable anchored walk, with behind-leg motion still noted for a future pass.
`stable-v6-functional-baseline/` contains the locked desktop-functionality baseline for behavior and menu iterations.
`stable-v7-functional-awareness/` contains the first stable app-aware desktop version with expanded right-click commands.
`stable-v8-live-diagnostics/` contains the app-aware version with live-updating status diagnostics.

Open `index.html` in a browser to try it. Dex is rendered on canvas, so his sprite and behavior states are generated live rather than stored as fixed image frames.

## Current Behaviors

- Slowly trots around the simulated desktop.
- Sits, lays down, sleeps, patrols, paces, and drops a leash.
- Right-click menu supports attention, walking, zoomies, nap, wake, patrol, leash, sit/stay, resume, reset, always-on-top, pause, and exit.
- Right-click menu includes `Show status` for current mode, pose, detected app, reaction, CPU, and always-on-top state.
- The always-on-top menu item shows `yes` or `no`.
- Desktop overlay detects the foreground Windows app/window title read-only.
- Reacts to Excel, PowerPoint, VSCode, terminals, Docker Desktop, Node-RED, Ignition, Teams/Zoom, and CPU spikes.
- Gets more persistent after long inactivity.
- Can be dragged around the screen as a short walk.
- Can enter midnight patrol and has rare zoomies.

## Files

- `index.html` - desktop simulation and controls.
- `styles.css` - retro industrial UI and responsive layout.
- `dex.js` - canvas sprite renderer, animation states, and behavior profile.
- `dex_desktop.py` - dependency-free Windows desktop overlay trial.
- `run_dex.bat` - double-click launcher for the desktop overlay.

## Desktop Trial

Double-click `run_dex.bat` to let Dex run around on the actual desktop. Left-drag him to walk him. Right-click Dex for attention, zoomies, or exit.

## Nice-to-Haves

- Add a visible checked/unchecked indication for `Toggle always on top`, such as an on/off label or checkmark in the right-click menu.
- Add a richer diagnostics window with manual test buttons for Excel, PowerPoint, Teams/Zoom, and engineering-tool reactions.

For all-day use, put a shortcut to `run_dex.bat` in the Windows Startup folder:

```text
Win + R -> shell:startup
```

Then paste a shortcut there.
