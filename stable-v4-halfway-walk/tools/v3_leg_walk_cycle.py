import os
from pathlib import Path

from cut_concept_sprites import mirror, read_png, write_png


def find_project_dir():
    """Resolve the nearest project/snapshot root; never trust the caller's cwd."""
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "assets" / "dex-concept").is_dir():
            return candidate
    raise RuntimeError("Refusing asset changes: project assets directory not found")


PROJECT_DIR = find_project_dir()


ASSET_DIR = str(PROJECT_DIR / "assets" / "dex-concept")
STABLE_DIR = str(PROJECT_DIR / "stable-v3" / "assets" / "dex-concept")
W, H = 184, 128


LEG_ZONES = [
    (31, 84, 61, 121),
    (75, 84, 103, 121),
    (127, 84, 157, 121),
]


def alpha(px):
    return px[3]


def extract_leg_pixels(base):
    legs = []
    for zone in LEG_ZONES:
        x0, y0, x1, y1 = zone
        pixels = []
        for y in range(y0, y1):
            for x in range(x0, x1):
                px = base[y][x]
                if alpha(px) > 20:
                    pixels.append((x, y, px))
        legs.append((zone, pixels))
    return legs


def clear_leg_pixels(rows, legs):
    for _zone, pixels in legs:
        for x, y, _px in pixels:
            rows[y][x] = (0, 0, 0, 0)


def paste_shifted(rows, pixels, dx, dy):
    for x, y, px in pixels:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < W and 0 <= ny < H:
            rows[ny][nx] = px


def draw_frame(base, phase):
    rows = [row[:] for row in base]
    legs = extract_leg_pixels(base)
    clear_leg_pixels(rows, legs)

    # Shift only original v3 lower-leg pixels. The offsets are intentionally
    # small; this gives readable footfalls without changing Dex's identity.
    offsets = [
        [(0, 0), (0, 0), (0, 0)],
        [(-3, 0), (2, -1), (3, 0)],
        [(0, -1), (0, 1), (0, -1)],
        [(3, 0), (-2, -1), (-3, 0)],
    ]

    for (_zone, pixels), (dx, dy) in zip(legs, offsets[phase]):
        paste_shifted(rows, pixels, dx, dy)

    return rows


def restore_static_assets():
    os.makedirs(ASSET_DIR, exist_ok=True)
    for name in os.listdir(ASSET_DIR):
        if name.endswith(".png"):
            os.remove(os.path.join(ASSET_DIR, name))
    for name in os.listdir(STABLE_DIR):
        if name.endswith(".png"):
            _w, _h, rows = read_png(os.path.join(STABLE_DIR, name))
            write_png(os.path.join(ASSET_DIR, name), W, H, rows)


def main():
    restore_static_assets()
    _w, _h, base = read_png(os.path.join(STABLE_DIR, "trot_0.png"))
    for phase in range(4):
        rows = draw_frame(base, phase)
        for pose in ("trot", "happy", "patrol", "zoom"):
            write_png(os.path.join(ASSET_DIR, f"{pose}_{phase}.png"), W, H, rows)
            write_png(os.path.join(ASSET_DIR, f"{pose}_{phase}_left.png"), W, H, mirror(rows))


if __name__ == "__main__":
    main()
