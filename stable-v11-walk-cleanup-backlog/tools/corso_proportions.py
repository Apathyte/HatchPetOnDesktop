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
SOURCE_DIR = str(PROJECT_DIR / "stable-v3" / "assets" / "dex-concept")
BASE_DIR = str(PROJECT_DIR / "assets" / "dex-corso-base")
W, H = 184, 128


def clone(rows):
    return [row[:] for row in rows]


def shift_for_pixel(x, y):
    # Keep the liked face/head and legs mostly fixed. Only the upper torso,
    # rear body, and tail get shifted enough to read longer-backed.
    if y < 20 or y > 84:
        return 0
    if x < 58:
        return 0
    if x < 135:
        return round((x - 58) / 77 * 6)
    return 6


def transform_rows(rows):
    out = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]
    for y, row in enumerate(rows):
        for x, px in enumerate(row):
            if px[3] <= 0:
                continue
            nx = x + shift_for_pixel(x, y)
            if 0 <= nx < W:
                out[y][nx] = px

    fill_torso_gaps(out)
    extend_tail(out)
    return out


def fill_torso_gaps(rows):
    # After progressive shifting, small transparent vertical cracks can appear
    # inside the body. Fill only pixels surrounded by coat, not outside air.
    for y in range(22, 96):
        for x in range(56, 158):
            if rows[y][x][3] > 20:
                continue
            left = nearest_opaque(rows, x, y, -1)
            right = nearest_opaque(rows, x, y, 1)
            if left and right and left[0] >= x - 10 and right[0] <= x + 10:
                rows[y][x] = mix(left[1], right[1])


def nearest_opaque(rows, x, y, direction):
    for step in range(1, 11):
        nx = x + step * direction
        if 0 <= nx < W and rows[y][nx][3] > 120:
            return nx, rows[y][nx]
    return None


def mix(a, b):
    return (
        (a[0] + b[0]) // 2,
        (a[1] + b[1]) // 2,
        (a[2] + b[2]) // 2,
        max(a[3], b[3]),
    )


def extend_tail(rows):
    # The current tail is readable but a bit short/compact. Add a few pixels at
    # the outer curl by extending existing tail pixels rightward, preserving color.
    additions = []
    for y in range(22, 74):
        for x in range(132, 174):
            px = rows[y][x]
            if px[3] > 80:
                for dx in (1, 2):
                    nx = x + dx
                    if nx < W and rows[y][nx][3] < 30:
                        additions.append((nx, y, fade(px, 0.82 if dx == 1 else 0.62)))
    for x, y, px in additions:
        rows[y][x] = px


def fade(px, amount):
    return (px[0], px[1], px[2], int(px[3] * amount))


def write_base_assets():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(ASSET_DIR, exist_ok=True)
    for name in os.listdir(ASSET_DIR):
        if name.endswith(".png"):
            os.remove(os.path.join(ASSET_DIR, name))

    for name in os.listdir(SOURCE_DIR):
        if not name.endswith(".png") or name.endswith("_left.png"):
            continue
        _w, _h, rows = read_png(os.path.join(SOURCE_DIR, name))
        transformed = transform_rows(rows)
        out_name = name
        left_name = name.replace(".png", "_left.png")
        write_png(os.path.join(BASE_DIR, out_name), W, H, transformed)
        write_png(os.path.join(BASE_DIR, left_name), W, H, mirror(transformed))
        write_png(os.path.join(ASSET_DIR, out_name), W, H, transformed)
        write_png(os.path.join(ASSET_DIR, left_name), W, H, mirror(transformed))


def main():
    write_base_assets()


if __name__ == "__main__":
    main()
