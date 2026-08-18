import math
import os
import struct
import zlib


OUT_DIR = os.path.join("assets", "dex")
W, H = 160, 112
SS = 4
HW, HH = W * SS, H * SS


def rgba(hex_color, alpha=255):
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
        alpha,
    )


def blend(dst, src):
    sr, sg, sb, sa = src
    if sa == 0:
        return dst
    dr, dg, db, da = dst
    a = sa / 255
    out_a = a + da / 255 * (1 - a)
    if out_a == 0:
        return (0, 0, 0, 0)
    return (
        int((sr * a + dr * da / 255 * (1 - a)) / out_a),
        int((sg * a + dg * da / 255 * (1 - a)) / out_a),
        int((sb * a + db * da / 255 * (1 - a)) / out_a),
        int(out_a * 255),
    )


def new_img():
    return [(0, 0, 0, 0)] * (HW * HH)


def set_px(img, x, y, color):
    if 0 <= x < HW and 0 <= y < HH:
        img[y * HW + x] = blend(img[y * HW + x], color)


def ellipse(img, cx, cy, rx, ry, color):
    cx, cy, rx, ry = [v * SS for v in (cx, cy, rx, ry)]
    x0, x1 = int(cx - rx), int(cx + rx)
    y0, y1 = int(cy - ry), int(cy + ry)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                set_px(img, x, y, color)


def rect(img, x, y, w, h, color):
    x, y, w, h = [int(v * SS) for v in (x, y, w, h)]
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(img, xx, yy, color)


def poly(img, points, color):
    pts = [(int(x * SS), int(y * SS)) for x, y in points]
    min_x = min(x for x, _ in pts)
    max_x = max(x for x, _ in pts)
    min_y = min(y for _, y in pts)
    max_y = max(y for _, y in pts)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            inside = False
            j = len(pts) - 1
            for i, (xi, yi) in enumerate(pts):
                xj, yj = pts[j]
                if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / (yj - yi + 0.0001) + xi:
                    inside = not inside
                j = i
            if inside:
                set_px(img, x, y, color)


def downsample(img):
    out = bytearray()
    for y in range(H):
        for x in range(W):
            r = g = b = a = 0
            for yy in range(SS):
                for xx in range(SS):
                    pr, pg, pb, pa = img[(y * SS + yy) * HW + (x * SS + xx)]
                    r += pr
                    g += pg
                    b += pb
                    a += pa
            div = SS * SS
            out.extend((r // div, g // div, b // div, a // div))
    return bytes(out)


def write_png(path, pixels):
    raw = b"".join(b"\x00" + pixels[y * W * 4 : (y + 1) * W * 4] for y in range(H))

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def mirror_pixels(pixels):
    out = bytearray(len(pixels))
    stride = W * 4
    for y in range(H):
        row = pixels[y * stride : (y + 1) * stride]
        for x in range(W):
            src = x * 4
            dst = (W - 1 - x) * 4
            out[y * stride + dst : y * stride + dst + 4] = row[src : src + 4]
    return bytes(out)


def draw_dex(pose, frame):
    img = new_img()
    outline = rgba("#111214")
    coat = rgba("#262626")
    coat_mid = rgba("#343331")
    coat_hi = rgba("#47423d")
    brindle = rgba("#6a4c3e")
    muzzle = rgba("#bfb8ad")
    muzzle_hi = rgba("#ded5c6")
    ear = rgba("#191919")
    eye = rgba("#17100b")
    glint = rgba("#fff5e6")
    nose = rgba("#080808")
    tongue = rgba("#c97975")
    vest = rgba("#e0a92d")
    vest_dark = rgba("#9c6620")
    vest_hi = rgba("#f3d466")

    bob = 0 if pose in {"sleep", "leash"} else math.sin(frame / 4 * math.tau) * 2
    step = math.sin(frame / 4 * math.tau)
    wag = math.sin(frame / 4 * math.tau) * (8 if pose == "happy" else 4)

    if pose == "sleep":
        body_y = 61
        head_y = 58
        ellipse(img, 73, body_y + 18, 49, 18, outline)
        ellipse(img, 74, body_y + 15, 44, 15, coat)
        ellipse(img, 72, body_y + 9, 29, 8, coat_mid)
        ellipse(img, 52, 81, 25, 6, outline)
        ellipse(img, 94, 81, 25, 6, outline)
    else:
        body_y = 54 + bob
        head_y = 35 + bob
        ellipse(img, 74, body_y, 46, 27, outline)
        ellipse(img, 75, body_y - 2, 41, 24, coat)
        ellipse(img, 69, body_y - 13, 28, 10, coat_mid)
        ellipse(img, 78, body_y - 2, 22, 8, brindle)
        ellipse(img, 94, body_y + 4, 16, 9, coat_hi)

        leg_positions = [(49, step), (75, -step), (99, step * 0.8)]
        for x, phase in leg_positions:
            leg_h = 24 + phase * 3
            rect(img, x - 5, body_y + 17, 12, leg_h, outline)
            rect(img, x - 3, body_y + 17, 8, leg_h, ear)
            ellipse(img, x + 1, body_y + 40 + phase * 2, 11, 5, muzzle_hi)

    # Tail, long and curled upward.
    ty = body_y - 11 + wag * 0.25
    ellipse(img, 29, ty + 24, 21, 9, outline)
    ellipse(img, 21, ty + 14, 15, 9, outline)
    ellipse(img, 24, ty + 6, 12, 9, outline)
    ellipse(img, 31, ty + 24, 17, 6, coat)
    ellipse(img, 22, ty + 15, 11, 6, coat)
    ellipse(img, 25, ty + 7, 8, 6, muzzle_hi)

    # Head and ears.
    ellipse(img, 111, head_y + 14, 23, 24, outline)
    ellipse(img, 111, head_y + 13, 20, 21, coat)
    ellipse(img, 109, head_y + 5, 14, 8, coat_mid)
    ellipse(img, 98, head_y + 14, 9, 18, outline)
    ellipse(img, 99, head_y + 15, 6, 15, ear)
    ellipse(img, 125, head_y + 13, 9, 18, outline)
    ellipse(img, 125, head_y + 14, 6, 15, ear)
    ellipse(img, 119, head_y + 23, 17, 13, muzzle)
    ellipse(img, 124, head_y + 28, 12, 8, muzzle_hi)
    ellipse(img, 126, head_y + 30, 4, 3, nose)

    if pose == "sleep":
        rect(img, 117, head_y + 17, 8, 2, eye)
        rect(img, 137, head_y - 7, 8, 3, muzzle_hi)
        rect(img, 148, head_y - 14, 5, 2, muzzle_hi)
    else:
        ellipse(img, 117, head_y + 15, 4, 5, eye)
        ellipse(img, 116, head_y + 14, 1.2, 1.2, glint)
        ellipse(img, 109, head_y + 16, 2, 3, rgba("#211b17"))
        if pose != "leash":
            ellipse(img, 128, head_y + 36, 4, 7, tongue)

    if pose in {"trot", "happy", "patrol"}:
        poly(img, [(55, body_y - 10), (94, body_y - 8), (98, body_y + 10), (62, body_y + 11)], vest)
        poly(img, [(91, body_y - 7), (101, body_y - 3), (99, body_y + 10), (92, body_y + 9)], vest_dark)
        rect(img, 66, body_y - 1, 18, 4, vest_hi)

    if pose == "leash":
        rect(img, 127, body_y + 22, 23, 4, rgba("#8b5a3d"))
        ellipse(img, 150, body_y + 19, 8, 8, rgba("#8b5a3d"))

    return downsample(img)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    poses = {
        "trot": 4,
        "happy": 4,
        "patrol": 4,
        "sleep": 2,
        "leash": 2,
        "zoom": 4,
    }
    for pose, count in poses.items():
        for frame in range(count):
            pixels = draw_dex(pose, frame)
            write_png(os.path.join(OUT_DIR, f"{pose}_{frame}.png"), pixels)
            write_png(os.path.join(OUT_DIR, f"{pose}_{frame}_left.png"), mirror_pixels(pixels))


if __name__ == "__main__":
    main()
