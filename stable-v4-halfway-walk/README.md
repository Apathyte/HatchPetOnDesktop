# Dex Desktop Pet

Dex is a static browser prototype for a pixel-art workstation companion: a stocky charcoal-black Cane Corso and pit bull mix with an old grey muzzle, calm protector energy, and engineering-shop personality.

`stable-v1/` contains the first stable desktop trial.
`stable-v2/` contains the improved hand-drawn Tkinter version.
`stable-v3/` contains the liked concept-sprite version before grounded-motion experiments.

Open `index.html` in a browser to try it. Dex is rendered on canvas, so his sprite and behavior states are generated live rather than stored as fixed image frames.

## Current Behaviors

- Slowly trots around the simulated desktop.
- Sits, lays down, sleeps, patrols, paces, and drops a leash.
- Reacts to active app selection: terminal, VSCode, Docker, Node-RED, Ignition, PowerPoint, Excel, and meetings.
- Wears a tiny hardhat or safety vest around engineering tools.
- Wakes up when CPU activity is high.
- Gets more persistent after long inactivity.
- Can be dragged around the screen as a short walk.
- Reacts to notifications, can enter midnight patrol, and has rare zoomies.

## Files

- `index.html` - desktop simulation and controls.
- `styles.css` - retro industrial UI and responsive layout.
- `dex.js` - canvas sprite renderer, animation states, and behavior profile.
- `dex_desktop.py` - dependency-free Windows desktop overlay trial.
- `run_dex.bat` - double-click launcher for the desktop overlay.

## Desktop Trial

Double-click `run_dex.bat` to let Dex run around on the actual desktop. Left-drag him to walk him. Right-click Dex for attention, zoomies, or exit.

For all-day use, put a shortcut to `run_dex.bat` in the Windows Startup folder:

```text
Win + R -> shell:startup
```

Then paste a shortcut there.
