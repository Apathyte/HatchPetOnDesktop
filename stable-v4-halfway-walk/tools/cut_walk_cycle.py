import os
from pathlib import Path

from cut_concept_sprites import mirror, read_png, remove_bg, resize_fit, trim_subject, write_png


def find_project_dir():
    """Resolve the nearest project/snapshot root; never trust the caller's cwd."""
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "assets" / "dex-concept").is_dir():
            return candidate
    raise RuntimeError("Refusing asset changes: project assets directory not found")


PROJECT_DIR = find_project_dir()


SRC = str(PROJECT_DIR / "assets" / "concepts" / "dex-walk-cycle-v1.png")
OUT = str(PROJECT_DIR / "assets" / "dex-concept")
TARGET_W = 184
TARGET_H = 128


def crop(rows, box):
    x0, y0, x1, y1 = box
    return [row[x0:x1] for row in rows[y0:y1]]


def remove_ground_line(rows):
    out = [row[:] for row in rows]
    width = len(out[0])
    for y, row in enumerate(out):
        grey_line_x = []
        for x, (r, g, b, a) in enumerate(row):
            avg = (r + g + b) / 3
            spread = max(r, g, b) - min(r, g, b)
            if a > 20 and 55 < avg < 215 and spread < 30:
                grey_line_x.append(x)
        if len(grey_line_x) > width * 0.16:
            for x in grey_line_x:
                for yy in range(max(0, y - 1), min(len(out), y + 2)):
                    out[yy][x] = (0, 0, 0, 0)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    _w, _h, rows = read_png(SRC)
    boxes = [
        (25, 165, 575, 620),
        (600, 165, 1085, 620),
        (1110, 165, 1645, 620),
        (1680, 165, 2135, 620),
    ]
    for i, box in enumerate(boxes):
        cut = trim_subject(crop(rows, box))
        cut = remove_bg(cut)
        cut = remove_ground_line(cut)
        sprite = resize_fit(cut, TARGET_W, TARGET_H)
        for pose in ("trot", "happy", "patrol", "zoom"):
            write_png(os.path.join(OUT, f"{pose}_{i}.png"), TARGET_W, TARGET_H, sprite)
            write_png(os.path.join(OUT, f"{pose}_{i}_left.png"), TARGET_W, TARGET_H, mirror(sprite))


if __name__ == "__main__":
    main()
