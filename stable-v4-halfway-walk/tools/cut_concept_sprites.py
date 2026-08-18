import os
import struct
import zlib


SRC = os.path.join("assets", "concepts", "dex-concept-spike-reference-v1.png")
OUT = os.path.join("assets", "dex-concept")
TARGET_W = 184
TARGET_H = 128


def paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def read_png(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos = 8
    width = height = color_type = None
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        payload = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, *_ = struct.unpack(">IIBBBBB", payload)
            if bit_depth != 8 or color_type not in (2, 6):
                raise ValueError("only 8-bit RGB/RGBA PNGs are supported")
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            break

    channels = 4 if color_type == 6 else 3
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    rows = []
    i = 0
    prev = [0] * stride
    for _ in range(height):
        ftype = raw[i]
        i += 1
        row = list(raw[i : i + stride])
        i += stride
        recon = [0] * stride
        for x, val in enumerate(row):
            left = recon[x - channels] if x >= channels else 0
            up = prev[x]
            up_left = prev[x - channels] if x >= channels else 0
            if ftype == 0:
                recon[x] = val
            elif ftype == 1:
                recon[x] = (val + left) & 255
            elif ftype == 2:
                recon[x] = (val + up) & 255
            elif ftype == 3:
                recon[x] = (val + ((left + up) // 2)) & 255
            elif ftype == 4:
                recon[x] = (val + paeth(left, up, up_left)) & 255
            else:
                raise ValueError("bad PNG filter")
        prev = recon
        rgba = []
        if channels == 4:
            for x in range(0, stride, 4):
                rgba.append(tuple(recon[x : x + 4]))
        else:
            for x in range(0, stride, 3):
                rgba.append((recon[x], recon[x + 1], recon[x + 2], 255))
        rows.append(rgba)
    return width, height, rows


def write_png(path, width, height, rows):
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for px in row:
            raw.extend(px)

    def chunk(kind, payload):
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def crop(rows, box):
    x0, y0, x1, y1 = box
    return [row[x0:x1] for row in rows[y0:y1]]


def background_alpha(r, g, b):
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    # Keep bright muzzle/chest pixels if they have enough grey detail.
    if avg > 247 and spread < 10:
        return 0
    if avg > 236 and spread < 12:
        return int((247 - avg) / 11 * 255)
    return 255


def trim_subject(rows):
    points = []
    for y, row in enumerate(rows):
        for x, (r, g, b, a) in enumerate(row):
            if a > 20 and background_alpha(r, g, b) > 20:
                points.append((x, y))
    if not points:
        return rows
    min_x = max(0, min(x for x, _ in points) - 12)
    max_x = min(len(rows[0]), max(x for x, _ in points) + 13)
    min_y = max(0, min(y for _, y in points) - 12)
    max_y = min(len(rows), max(y for _, y in points) + 13)
    return crop(rows, (min_x, min_y, max_x, max_y))


def remove_bg(rows):
    h = len(rows)
    w = len(rows[0])
    seen = [[False for _ in range(w)] for _ in range(h)]
    stack = []
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h - 1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w - 1, y))

    def is_bg(px):
        r, g, b, _a = px
        avg = (r + g + b) / 3
        spread = max(r, g, b) - min(r, g, b)
        return avg > 210 and spread < 28

    while stack:
        x, y = stack.pop()
        if not (0 <= x < w and 0 <= y < h) or seen[y][x]:
            continue
        if not is_bg(rows[y][x]):
            continue
        seen[y][x] = True
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    out = []
    for y, row in enumerate(rows):
        out_row = []
        for x, (r, g, b, a) in enumerate(row):
            if seen[y][x]:
                out_row.append((r, g, b, 0))
            else:
                out_row.append((r, g, b, a))
        out.append(out_row)
    return out


def resize_fit(rows, width, height):
    src_h = len(rows)
    src_w = len(rows[0])
    scale = min(width / src_w, height / src_h)
    new_w = max(1, int(src_w * scale))
    new_h = max(1, int(src_h * scale))
    resized = [[(0, 0, 0, 0) for _ in range(width)] for _ in range(height)]
    off_x = (width - new_w) // 2
    off_y = height - new_h
    for y in range(new_h):
        sy = min(src_h - 1, int(y / scale))
        for x in range(new_w):
            sx = min(src_w - 1, int(x / scale))
            resized[off_y + y][off_x + x] = rows[sy][sx]
    return resized


def mirror(rows):
    return [list(reversed(row)) for row in rows]


def main():
    os.makedirs(OUT, exist_ok=True)
    _w, _h, rows = read_png(SRC)
    boxes = {
        "idle": (20, 205, 520, 700),
        "sit": (520, 185, 850, 705),
        "sleep": (845, 445, 1270, 705),
        "trot": (1260, 215, 1750, 710),
    }
    mapping = {
        "idle": ["trot_0", "patrol_0", "leash_0"],
        "sit": ["sit_0"],
        "sleep": ["sleep_0"],
        "trot": ["happy_0", "zoom_0"],
    }
    for pose, box in boxes.items():
        cut = trim_subject(crop(rows, box))
        cut = remove_bg(cut)
        sprite = resize_fit(cut, TARGET_W, TARGET_H)
        for name in mapping[pose]:
            write_png(os.path.join(OUT, f"{name}.png"), TARGET_W, TARGET_H, sprite)
            write_png(os.path.join(OUT, f"{name}_left.png"), TARGET_W, TARGET_H, mirror(sprite))


if __name__ == "__main__":
    main()
