import os
from pathlib import Path

from cut_concept_sprites import read_png, write_png




def find_project_dir():
    """Resolve the nearest project/snapshot root; never trust the caller's cwd."""
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "assets" / "dex-concept").is_dir():
            return candidate
    raise RuntimeError("Refusing asset changes: project assets directory not found")


PROJECT_DIR = find_project_dir()
ASSET_DIR = str(PROJECT_DIR / "assets" / "dex-concept")
W, H = 184, 128


def blend(dst, src):
    sr, sg, sb, sa = src
    dr, dg, db, da = dst
    a = sa / 255
    out_a = a + da / 255 * (1 - a)
    if out_a <= 0:
        return (0, 0, 0, 0)
    return (
        int((sr * a + dr * da / 255 * (1 - a)) / out_a),
        int((sg * a + dg * da / 255 * (1 - a)) / out_a),
        int((sb * a + db * da / 255 * (1 - a)) / out_a),
        int(out_a * 255),
    )


def ellipse_mask(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1


def is_background_or_light(px):
    r, g, b, a = px
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    return a < 80 or (avg > 135 and spread < 80)


def fill_rows(rows, mirrored=False):
    out = [row[:] for row in rows]
    dark_belly = (35, 34, 32, 255)
    dark_edge = (18, 18, 18, 230)

    # Coordinates are for the accepted left-facing v3 concept sprite. Mirrored
    # frames are fixed by reflecting the same masks horizontally.
    masks = [
        (65, 76, 22, 18),
        (95, 86, 27, 17),
    ]

    for base_cx, cy, rx, ry in masks:
        cx = W - base_cx if mirrored else base_cx
        for y in range(max(0, int(cy - ry)), min(H, int(cy + ry + 1))):
            for x in range(max(0, int(cx - rx)), min(W, int(cx + rx + 1))):
                if not ellipse_mask(x, y, cx, cy, rx, ry):
                    continue
                current = out[y][x]
                if is_background_or_light(current):
                    out[y][x] = blend(current, dark_belly)

    # Add a thin dark bridge high under the chest so a desktop-colored hole
    # cannot show through between the front legs.
    x0, x1 = (45, 84) if not mirrored else (W - 84, W - 45)
    for y in range(66, 83):
        for x in range(x0, x1):
            if out[y][x][3] < 120:
                out[y][x] = dark_edge

    return out


def main():
    for name in os.listdir(ASSET_DIR):
        if not name.endswith(".png"):
            continue
        path = os.path.join(ASSET_DIR, name)
        w, h, rows = read_png(path)
        if (w, h) != (W, H):
            continue
        fixed = fill_rows(rows, mirrored=name.endswith("_left.png"))
        write_png(path, w, h, fixed)


if __name__ == "__main__":
    main()
