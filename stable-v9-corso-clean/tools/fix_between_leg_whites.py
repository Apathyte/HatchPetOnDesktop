import os

from cut_concept_sprites import read_png, write_png


ASSET_DIR = os.path.join("assets", "dex-concept")
W, H = 184, 128


def soften_light_gap(px, strength):
    r, g, b, a = px
    if a < 20:
        return px
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    if avg < 155 or spread > 60:
        return px

    target = (43, 42, 39)
    nr = int(r * (1 - strength) + target[0] * strength)
    ng = int(g * (1 - strength) + target[1] * strength)
    nb = int(b * (1 - strength) + target[2] * strength)
    return (nr, ng, nb, a)


def fix_rows(rows):
    out = [row[:] for row in rows]

    # Active left-facing v3 sprite: lower chest/belly gap between the front legs.
    # The paws are lower than this and are intentionally left untouched.
    boxes = [
        (45, 58, 82, 88, 0.82),
        (76, 69, 123, 94, 0.72),
    ]

    for x0, y0, x1, y1, strength in boxes:
        for y in range(y0, min(y1, len(out))):
            for x in range(x0, min(x1, len(out[0]))):
                out[y][x] = soften_light_gap(out[y][x], strength)

    return out


def main():
    for name in os.listdir(ASSET_DIR):
        if not name.endswith(".png"):
            continue
        path = os.path.join(ASSET_DIR, name)
        w, h, rows = read_png(path)
        if (w, h) != (W, H):
            continue
        write_png(path, w, h, fix_rows(rows))


if __name__ == "__main__":
    main()
