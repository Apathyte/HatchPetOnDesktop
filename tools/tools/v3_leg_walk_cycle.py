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
SOURCE_DIR = str(PROJECT_DIR / "assets" / "dex-corso-base")
FALLBACK_DIR = str(PROJECT_DIR / "stable-v3" / "assets" / "dex-concept")
W, H = 184, 128


LEG_ZONES = [
    (30, 86, 58, 121),
    (54, 86, 78, 121),
    (76, 86, 104, 121),
    (126, 86, 158, 121),
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


def paste_shifted(rows, pixels, dx, dy):
    for x, y, px in pixels:
        # Keep the original v3 leg in place as the anchor. Overlay motion only
        # from the lower leg down so animation cannot expose white seams.
        if y < 96:
            continue
        if y < 107:
            weight = 0.45
        else:
            weight = 1.0
        nx = x + round(dx * weight)
        ny = y + dy
        if 0 <= nx < W and 0 <= ny < H:
            rows[ny][nx] = px


def draw_frame(base, phase):
    rows = [row[:] for row in base]
    legs = extract_leg_pixels(base)

    # Shift only original v3 lower-leg pixels. The offsets are intentionally
    # small; this gives readable footfalls without changing Dex's identity.
    offsets = [
        [(0, 0), (2, 0), (0, 0), (-2, 0)],
        [(-3, 0), (3, -1), (2, -1), (3, 0)],
        [(0, -1), (0, 1), (0, -1), (0, 1)],
        [(3, 0), (-3, -1), (-2, -1), (-3, 0)],
    ]

    for (_zone, pixels), (dx, dy) in zip(legs, offsets[phase]):
        paste_shifted(rows, pixels, dx, dy)

    return rows


def restore_static_assets():
    source_dir = SOURCE_DIR if os.path.isdir(SOURCE_DIR) else FALLBACK_DIR
    os.makedirs(ASSET_DIR, exist_ok=True)
    for name in os.listdir(ASSET_DIR):
        if name.endswith(".png"):
            os.remove(os.path.join(ASSET_DIR, name))
    for name in os.listdir(source_dir):
        if name.endswith(".png"):
            _w, _h, rows = read_png(os.path.join(source_dir, name))
            write_png(os.path.join(ASSET_DIR, name), W, H, rows)


def main():
    restore_static_assets()
    source_dir = SOURCE_DIR if os.path.isdir(SOURCE_DIR) else FALLBACK_DIR
    _w, _h, base = read_png(os.path.join(source_dir, "trot_0.png"))
    for phase in range(4):
        rows = draw_frame(base, phase)
        for pose in ("trot", "happy", "patrol", "zoom"):
            write_png(os.path.join(ASSET_DIR, f"{pose}_{phase}.png"), W, H, rows)
            write_png(os.path.join(ASSET_DIR, f"{pose}_{phase}_left.png"), W, H, mirror(rows))


if __name__ == "__main__":
    main()
