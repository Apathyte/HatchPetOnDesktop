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


def in_poly(x, y, points):
    inside = False
    j = len(points) - 1
    for i, (xi, yi) in enumerate(points):
        xj, yj = points[j]
        if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / (yj - yi + 0.0001) + xi:
            inside = not inside
        j = i
    return inside


def reflect(points):
    return [(W - x, y) for x, y in points]


def should_replace(px):
    r, g, b, a = px
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    # This catches white/grey background or chest spill, plus transparent holes
    # that become visually bright on light windows behind Dex.
    return a < 210 or (avg > 118 and spread < 95)


def coat_tone(x, y):
    # Slightly varied dark brindle so the fill does not look like a flat blob.
    if (x + y) % 7 in (0, 1):
        return (62, 49, 41, 255)
    if (x + y) % 5 == 0:
        return (42, 39, 36, 255)
    return (29, 29, 28, 255)


def fix(rows, mirrored):
    out = [row[:] for row in rows]

    # Right-facing sprite gap, drawn around the visible belly space between
    # the legs in the screenshot. Non-mirrored sprites use the reflected mask.
    gap = [
        (43, 74),
        (112, 74),
        (126, 100),
        (111, 118),
        (45, 118),
        (35, 98),
    ]
    mask = gap if mirrored else reflect(gap)

    for y in range(68, 122):
        for x in range(24, 140):
            if in_poly(x, y, mask) and should_replace(out[y][x]):
                out[y][x] = coat_tone(x, y)

    # A narrower hard cleanup for the exact light sliver that tends to remain
    # under the chest/front-leg junction.
    sliver = (50, 82, 103, 114) if mirrored else (W - 103, 82, W - 50, 114)
    x0, y0, x1, y1 = sliver
    for y in range(y0, y1):
        for x in range(x0, x1):
            if should_replace(out[y][x]):
                out[y][x] = coat_tone(x, y)

    return out


def main():
    for name in os.listdir(ASSET_DIR):
        if not name.endswith(".png"):
            continue
        path = os.path.join(ASSET_DIR, name)
        w, h, rows = read_png(path)
        if (w, h) != (W, H):
            continue
        write_png(path, w, h, fix(rows, mirrored=name.endswith("_left.png")))


if __name__ == "__main__":
    main()
