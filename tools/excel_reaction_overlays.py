import os

from cut_concept_sprites import read_png, write_png


W, H = 184, 128
ASSET_DIR = os.path.join("assets", "dex-concept")
OVERLAY_DIR = os.path.join("assets", "dex-overlays")
PREVIEW_DIR = os.path.join("assets", "previews")


def blank():
    return [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]


def blend(dst, src):
    sr, sg, sb, sa = src
    dr, dg, db, da = dst
    if sa == 0:
        return dst
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


def line(rows, x0, y0, x1, y1, color, width=1):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    radius = max(0, width // 2)
    for i in range(steps + 1):
        t = i / steps
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        for yy in range(y - radius, y + radius + 1):
            for xx in range(x - radius, x + radius + 1):
                set_px(rows, xx, yy, color)


def rect(rows, x0, y0, x1, y1, color):
    for y in range(y0, y1):
        for x in range(x0, x1):
            set_px(rows, x, y, color)


def ellipse(rows, cx, cy, rx, ry, color):
    for y in range(int(cy - ry), int(cy + ry + 1)):
        for x in range(int(cx - rx), int(cx + rx + 1)):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                set_px(rows, x, y, color)


def mirror(rows):
    return [list(reversed(row)) for row in rows]


def composited(base, overlays):
    out = [row[:] for row in base]
    for overlay in overlays:
        for y in range(H):
            for x in range(W):
                out[y][x] = blend(out[y][x], overlay[y][x])
    return out


def on_background(rows, bg=(255, 255, 255)):
    out = []
    for row in rows:
        out_row = []
        for r, g, b, a in row:
            alpha = a / 255
            out_row.append(
                (
                    int(r * alpha + bg[0] * (1 - alpha)),
                    int(g * alpha + bg[1] * (1 - alpha)),
                    int(b * alpha + bg[2] * (1 - alpha)),
                    255,
                )
            )
        out.append(out_row)
    return out


def make_excel_overlays(facing="left"):
    # Coordinates are full-frame and aligned to the current sit sprite.
    # Keep these tiny; expression should read as a detail, not a new sprite.
    brow = blank()
    mouth = blank()
    sigh = blank()

    if facing == "left":
        line(brow, 52, 35, 62, 38, (226, 215, 193, 210), width=1)
        line(brow, 53, 36, 63, 39, (23, 18, 14, 245), width=1)
        line(mouth, 55, 60, 63, 59, (45, 35, 28, 225), width=1)
        line(sigh, 32, 54, 42, 54, (202, 194, 178, 210), width=1)
        line(sigh, 29, 59, 39, 59, (142, 134, 122, 185), width=1)
    else:
        line(brow, 122, 38, 132, 35, (226, 215, 193, 210), width=1)
        line(brow, 121, 39, 131, 36, (23, 18, 14, 245), width=1)
        line(mouth, 121, 59, 129, 60, (45, 35, 28, 225), width=1)
        line(sigh, 142, 54, 152, 54, (202, 194, 178, 210), width=1)
        line(sigh, 145, 59, 155, 59, (142, 134, 122, 185), width=1)

    return {
        "excel_brow": brow,
        "excel_mouth_tense": mouth,
        "excel_sigh": sigh,
    }


def make_excel_sigh_frames(facing="left"):
    frames = []
    for i in range(3):
        rows = blank()
        drift = i * 3
        alpha = 230 - i * 45
        if facing == "left":
            x0 = 25 - drift
            line(rows, x0 + 10, 44 - i, x0 + 24, 44 - i, (236, 230, 216, alpha), width=2)
            line(rows, x0 + 6, 50 - i, x0 + 19, 50 - i, (166, 158, 145, alpha), width=1)
            ellipse(rows, x0 + 27, 47 - i, 3, 2, (236, 230, 216, alpha))
        else:
            x0 = 136 + drift
            line(rows, x0, 44 - i, x0 + 14, 44 - i, (236, 230, 216, alpha), width=2)
            line(rows, x0 + 5, 50 - i, x0 + 18, 50 - i, (166, 158, 145, alpha), width=1)
            ellipse(rows, x0 - 4, 47 - i, 3, 2, (236, 230, 216, alpha))
        frames.append(rows)
    return frames


def main():
    os.makedirs(OVERLAY_DIR, exist_ok=True)
    os.makedirs(PREVIEW_DIR, exist_ok=True)

    for facing, suffix, base_name in [
        ("left", "_left", "sit_0_left.png"),
        ("right", "", "sit_0.png"),
    ]:
        overlays = make_excel_overlays(facing)
        for name, rows in overlays.items():
            write_png(os.path.join(OVERLAY_DIR, f"{name}{suffix}.png"), W, H, rows)

        for i, rows in enumerate(make_excel_sigh_frames(facing)):
            write_png(os.path.join(OVERLAY_DIR, f"excel_sigh_{i}{suffix}.png"), W, H, rows)

        _w, _h, base = read_png(os.path.join(ASSET_DIR, base_name))
        combo = composited(base, [overlays["excel_brow"], make_excel_sigh_frames(facing)[1]])
        write_png(os.path.join(PREVIEW_DIR, f"excel_reaction_preview{suffix}.png"), W, H, on_background(combo))
        write_png(os.path.join(PREVIEW_DIR, f"excel_reaction_preview_yellow{suffix}.png"), W, H, on_background(combo, bg=(255, 244, 196)))
        for i, sigh_frame in enumerate(make_excel_sigh_frames(facing)):
            frame = composited(base, [overlays["excel_brow"], sigh_frame])
            write_png(os.path.join(PREVIEW_DIR, f"excel_reaction_preview_{i}{suffix}.png"), W, H, on_background(frame))
            write_png(os.path.join(PREVIEW_DIR, f"excel_reaction_preview_yellow_{i}{suffix}.png"), W, H, on_background(frame, bg=(255, 244, 196)))


if __name__ == "__main__":
    main()
