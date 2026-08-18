import os

from cut_concept_sprites import mirror, read_png, write_png


ASSET_DIR = os.path.join("assets", "dex-concept")
STABLE_DIR = os.path.join("stable-v3", "assets", "dex-concept")
W, H = 184, 128


def clone(rows):
    return [row[:] for row in rows]


def alpha(px):
    return px[3]


def is_ground_line(px):
    r, g, b, a = px
    if a < 20:
        return False
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    return 55 < avg < 210 and spread < 32


def clear_boxes(rows, boxes):
    for x0, y0, x1, y1 in boxes:
        for y in range(y0, min(y1, len(rows))):
            for x in range(x0, min(x1, len(rows[0]))):
                if alpha(rows[y][x]) > 20:
                    rows[y][x] = (0, 0, 0, 0)


def paste_leg_pixels(base, donor, y_min=72):
    for y in range(y_min, H):
        for x in range(W):
            px = donor[y][x]
            if alpha(px) <= 20 or is_ground_line(px):
                continue
            # Only borrow the walking sheet where legs and paws live. Keeping
            # the v3 head, torso, bandana, tail and upper outline prevents L&F drift.
            if 18 <= x <= 166:
                base[y][x] = px


def copy_stable_static_assets():
    for name in os.listdir(STABLE_DIR):
        if name.endswith(".png"):
            _w, _h, rows = read_png(os.path.join(STABLE_DIR, name))
            write_png(os.path.join(ASSET_DIR, name), W, H, rows)


def main():
    os.makedirs(ASSET_DIR, exist_ok=True)

    # Keep a copy of the generated walk-cycle frames as donors before restoring.
    donors = []
    for i in range(4):
        path = os.path.join(ASSET_DIR, f"trot_{i}.png")
        if os.path.exists(path):
            _w, _h, rows = read_png(path)
            donors.append(rows)

    copy_stable_static_assets()
    _w, _h, stable = read_png(os.path.join(STABLE_DIR, "trot_0.png"))

    leg_boxes = [
        (28, 72, 58, 123),
        (60, 70, 92, 123),
        (108, 70, 149, 123),
    ]

    if len(donors) < 4:
        donors = [stable, stable, stable, stable]

    for i, donor in enumerate(donors[:4]):
        frame = clone(stable)
        clear_boxes(frame, leg_boxes)
        paste_leg_pixels(frame, donor)
        for pose in ("trot", "happy", "patrol", "zoom"):
            write_png(os.path.join(ASSET_DIR, f"{pose}_{i}.png"), W, H, frame)
            write_png(os.path.join(ASSET_DIR, f"{pose}_{i}_left.png"), W, H, mirror(frame))


if __name__ == "__main__":
    main()
