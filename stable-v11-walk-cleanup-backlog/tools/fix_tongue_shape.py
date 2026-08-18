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


def set_px(rows, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        rows[y][x] = blend(rows[y][x], color)


def ellipse(rows, cx, cy, rx, ry, color):
    for y in range(int(cy - ry), int(cy + ry + 1)):
        for x in range(int(cx - rx), int(cx + rx + 1)):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                set_px(rows, x, y, color)


def clear_box(rows, x0, y0, x1, y1):
    for y in range(y0, y1):
        for x in range(x0, x1):
            rows[y][x] = (0, 0, 0, 0)


def fix_left_facing(rows):
    # Remove the long horizontal tongue protrusion. At this sprite scale a tiny
    # replacement tongue quickly becomes a blob, so keep the mouth dark/clean.
    clear_box(rows, 48, 51, 66, 64)

    dark = (39, 31, 27, 245)
    ellipse(rows, 60, 54, 4, 3, dark)
    set_px(rows, 56, 55, (83, 54, 49, 220))
    return rows


def main():
    pairs = [
        ("sit_0_left.png", "sit_0.png"),
    ]
    for left_name, right_name in pairs:
        left_path = os.path.join(ASSET_DIR, left_name)
        if not os.path.exists(left_path):
            continue
        w, h, rows = read_png(left_path)
        fixed = fix_left_facing(rows)
        write_png(left_path, w, h, fixed)
        write_png(os.path.join(ASSET_DIR, right_name), w, h, mirror(fixed))


if __name__ == "__main__":
    main()
