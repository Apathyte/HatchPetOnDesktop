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
STABLE_DIR = str(PROJECT_DIR / "stable-v3" / "assets" / "dex-concept")
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


def blend(px, target, amount):
    r, g, b, a = px
    tr, tg, tb = target
    return (
        int(r * (1 - amount) + tr * amount),
        int(g * (1 - amount) + tg * amount),
        int(b * (1 - amount) + tb * amount),
        a,
    )


def is_bad_light(px):
    r, g, b, a = px
    if a < 80:
        return False
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    return avg > 168 and spread < 42


def cleanup(rows, mirrored):
    out = [row[:] for row in rows]

    # Very small zone only: the pale artifact below the belly, not paws,
    # not rear-leg silhouette, and not the chest/muzzle highlights.
    gap_right_facing = [
        (52, 82),
        (79, 78),
        (101, 88),
        (96, 101),
        (59, 101),
        (47, 91),
    ]
    mask = gap_right_facing if mirrored else reflect(gap_right_facing)

    for y in range(76, 106):
        for x in range(38, 114):
            if in_poly(x, y, mask) and is_bad_light(out[y][x]):
                out[y][x] = blend(out[y][x], (42, 38, 34), 0.78)

    return out


def main():
    # Always begin from the locked v3 assets so prior overpaint attempts cannot
    # accumulate into black blobs.
    os.makedirs(ASSET_DIR, exist_ok=True)
    for name in os.listdir(ASSET_DIR):
        if name.endswith(".png"):
            os.remove(os.path.join(ASSET_DIR, name))

    for name in os.listdir(STABLE_DIR):
        if not name.endswith(".png"):
            continue
        _w, _h, rows = read_png(os.path.join(STABLE_DIR, name))
        fixed = cleanup(rows, mirrored=name.endswith("_left.png"))
        write_png(os.path.join(ASSET_DIR, name), W, H, fixed)


if __name__ == "__main__":
    main()
