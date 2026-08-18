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


def has_opaque_neighbor(rows, x, y, radius=1):
    for yy in range(max(0, y - radius), min(H, y + radius + 1)):
        for xx in range(max(0, x - radius), min(W, x + radius + 1)):
            if xx == x and yy == y:
                continue
            if rows[yy][xx][3] > 220:
                return True
    return False


def should_keep_bright_detail(x, y):
    # Preserve face/muzzle eye glints, tongue, chest highlights and intentional
    # paw highlights. The cleanup targets accidental white specks elsewhere.
    if 104 <= x <= 150 and 24 <= y <= 76:
        return True
    if 62 <= x <= 92 and 40 <= y <= 72:
        return True
    if y >= 108:
        return True
    return False


def tone_down(px, target=(73, 66, 58), amount=0.72):
    r, g, b, a = px
    tr, tg, tb = target
    return (
        int(r * (1 - amount) + tr * amount),
        int(g * (1 - amount) + tg * amount),
        int(b * (1 - amount) + tb * amount),
        a,
    )


def clean(rows):
    out = [row[:] for row in rows]
    for y, row in enumerate(rows):
        for x, (r, g, b, a) in enumerate(row):
            if 0 < a < 96:
                out[y][x] = (0, 0, 0, 0)
                continue

            if 96 <= a < 210 and not has_opaque_neighbor(rows, x, y, radius=1):
                out[y][x] = (0, 0, 0, 0)
                continue

            if 96 <= a < 255:
                out[y][x] = (r, g, b, 255)
                a = 255

            avg = (r + g + b) / 3
            spread = max(r, g, b) - min(r, g, b)
            if a > 40 and avg > 202 and spread < 45 and not should_keep_bright_detail(x, y):
                out[y][x] = tone_down((r, g, b, a))

            if a > 40 and avg > 188 and spread < 34 and is_outer_edge_speck(rows, x, y):
                out[y][x] = tone_down((r, g, b, a), target=(38, 35, 31), amount=0.82)
    return out


def is_outer_edge_speck(rows, x, y):
    transparent_neighbors = 0
    for yy in range(max(0, y - 1), min(H, y + 2)):
        for xx in range(max(0, x - 1), min(W, x + 2)):
            if xx == x and yy == y:
                continue
            if rows[yy][xx][3] < 30:
                transparent_neighbors += 1
    return transparent_neighbors >= 4


def main():
    for name in os.listdir(ASSET_DIR):
        if not name.endswith(".png"):
            continue
        path = os.path.join(ASSET_DIR, name)
        w, h, rows = read_png(path)
        if (w, h) != (W, H):
            continue
        write_png(path, w, h, clean(rows))


if __name__ == "__main__":
    main()
