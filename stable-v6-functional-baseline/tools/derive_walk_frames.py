import os

from cut_concept_sprites import mirror, read_png, write_png


BASE = os.path.join("assets", "dex-concept")
WALK_POSES = ("trot", "happy", "patrol", "zoom")


def transparent_like(px):
    return px[3] < 18


def shift_region(rows, box, dx, dy):
    x0, y0, x1, y1 = box
    h = len(rows)
    w = len(rows[0])
    moved = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            px = rows[y][x]
            if not transparent_like(px):
                moved.append((x + dx, y + dy, px))
                rows[y][x] = (0, 0, 0, 0)
    for x, y, px in moved:
        if 0 <= x < w and 0 <= y < h:
            rows[y][x] = px


def clone(rows):
    return [row[:] for row in rows]


def derive_from(path, phase):
    _w, _h, base = read_png(path)
    rows = clone(base)

    # These boxes target the visible lower legs/paws in the concept-cut standing
    # sprite. Small shifts preserve the art while making footfalls readable.
    front_leg = (28, 76, 58, 121)
    chest_leg = (60, 72, 91, 121)
    rear_leg = (111, 70, 147, 121)

    if phase == 1:
        shift_region(rows, front_leg, 4, -1)
        shift_region(rows, chest_leg, -3, 1)
        shift_region(rows, rear_leg, -2, 0)
    elif phase == 2:
        shift_region(rows, front_leg, 0, 1)
        shift_region(rows, chest_leg, 0, -1)
        shift_region(rows, rear_leg, 0, 1)
    elif phase == 3:
        shift_region(rows, front_leg, -3, 1)
        shift_region(rows, chest_leg, 4, -1)
        shift_region(rows, rear_leg, 3, 0)

    return rows


def main():
    for pose in WALK_POSES:
        src = os.path.join(BASE, f"{pose}_0.png")
        if not os.path.exists(src):
            continue
        for phase in range(4):
            rows = derive_from(src, phase)
            write_png(os.path.join(BASE, f"{pose}_{phase}.png"), 184, 128, rows)
            write_png(os.path.join(BASE, f"{pose}_{phase}_left.png"), 184, 128, mirror(rows))


if __name__ == "__main__":
    main()
