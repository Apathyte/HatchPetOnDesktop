import math
import os
import random
import sys
import time
import tkinter as tk


TRANSPARENT = "#ff00ff"
SCALE = 2
PET_W = 188
PET_H = 132
DEX_VERSION = "art-v1-concept-cut"


class DexDesktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Dex")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT)

        if sys.platform.startswith("win"):
            self.root.wm_attributes("-transparentcolor", TRANSPARENT)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.canvas = tk.Canvas(
            self.root,
            width=PET_W,
            height=PET_H,
            bg=TRANSPARENT,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        self.x = 80
        self.y = max(80, self.screen_h - PET_H - 58)
        self.direction = 1
        self.dragging = False
        self.drag_dx = 0
        self.drag_dy = 0
        self.pose = "trot"
        self.item = "none"
        self.gear = "none"
        self.attention_until = 0
        self.zoomies_until = 0
        self.sleep_after = time.time() + 35 * 60
        self.last_walk = time.time()
        self.started = time.time()

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.canvas.bind("<Button-3>", self.show_menu)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Give attention", command=self.give_attention)
        self.menu.add_command(label="Walk Dex", command=self.walk)
        self.menu.add_command(label="Zoomies", command=self.zoomies)
        self.menu.add_separator()
        self.menu.add_command(label="Exit Dex", command=self.root.destroy)

        self.root.geometry(f"{PET_W}x{PET_H}+{self.x}+{self.y}")
        self.sprite_frames = self.load_sprite_frames()
        self.tick()

    def load_sprite_frames(self):
        base = os.path.join(os.path.dirname(__file__), "assets", "dex-concept")
        frames = {}
        for pose in ("trot", "happy", "patrol", "sleep", "leash", "zoom"):
            path = os.path.join(base, f"{pose}_0.png")
            left_path = os.path.join(base, f"{pose}_0_left.png")
            if os.path.exists(path):
                frames[pose] = [tk.PhotoImage(file=path)]
            if os.path.exists(left_path):
                frames[f"{pose}_left"] = [tk.PhotoImage(file=left_path)]
        return frames

    def start_drag(self, event):
        self.dragging = True
        self.drag_dx = event.x
        self.drag_dy = event.y
        self.walk()

    def drag(self, event):
        pointer_x = self.root.winfo_pointerx()
        pointer_y = self.root.winfo_pointery()
        self.x = pointer_x - self.drag_dx
        self.y = pointer_y - self.drag_dy
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.walk()

    def end_drag(self, _event):
        self.dragging = False

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def give_attention(self):
        self.attention_until = time.time() + 10
        self.sleep_after = time.time() + 35 * 60

    def walk(self):
        self.last_walk = time.time()
        self.attention_until = time.time() + 16
        self.sleep_after = time.time() + 35 * 60

    def zoomies(self):
        self.zoomies_until = time.time() + 4

    def choose_pose(self, now):
        inactive = now - self.last_walk
        self.pose = "trot"
        self.item = "none"
        self.gear = "none"

        if now > self.sleep_after:
            self.pose = "sleep"

        if inactive > 60 * 60:
            self.pose = "leash"
            self.item = "leash"

        hour = time.localtime().tm_hour
        if hour < 5 and self.pose == "trot":
            self.pose = "patrol"

        if now < self.attention_until:
            self.pose = "happy"

        if now < self.zoomies_until:
            self.pose = "zoom"

    def move(self, now):
        if self.dragging:
            return

        floor_y = self.screen_h - PET_H - 54
        target_y = floor_y + 22 if self.pose == "sleep" else floor_y
        self.y += (target_y - self.y) * 0.04

        if self.pose == "sleep":
            speed = 0
        elif self.pose == "zoom":
            speed = 10
        elif self.pose == "patrol":
            speed = 1.25
        elif self.pose == "leash":
            speed = 0.55
        else:
            speed = 0.42

        if self.pose == "leash":
            target_x = 24 if self.x < self.screen_w / 2 else self.screen_w - PET_W - 24
            self.x += (target_x - self.x) * 0.018
        else:
            self.x += speed * self.direction

        if self.x < 8:
            self.x = 8
            self.direction = 1
        elif self.x > self.screen_w - PET_W - 8:
            self.x = self.screen_w - PET_W - 8
            self.direction = -1

        if random.random() < 0.0009 and self.pose == "trot":
            self.zoomies()

        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    def rect(self, x, y, w, h, color):
        x *= SCALE
        y *= SCALE
        w *= SCALE
        h *= SCALE
        if self.direction == -1:
            x = PET_W - x - w
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline=color)

    def poly(self, points, color):
        scaled = []
        for x, y in points:
            x *= SCALE
            y *= SCALE
            if self.direction == -1:
                x = PET_W - x
            scaled.extend([x, y])
        self.canvas.create_polygon(scaled, fill=color, outline=color)

    def draw(self, now):
        if self.draw_sprite_frame():
            return

        self.canvas.delete("all")
        t = int(now * 6) % 4
        pant = int(now * 3.5) % 2
        laying = self.pose == "sleep"
        sit = self.pose == "leash"
        bob = 0 if laying else math.sin(now * 5) * 1.5
        wag = math.sin(now * (13 if self.pose == "happy" else 4)) * (7 if self.pose == "happy" else 3)

        outline = "#0b0c0d"
        charcoal = "#242424"
        black = "#141516"
        shadow = "#1b1c1d"
        shine = "#383838"
        brindle = "#46372d"
        brindle_light = "#60483b"
        grey = "#b8b2aa"
        warm_grey = "#d0c7ba"
        amber = "#d9a536"
        amber_shadow = "#a86f25"
        eye = "#130f0d"
        eye_glint = "#f3eadc"
        tongue = "#c67973"

        body_y = 34 if laying else 26 if sit else 25 + bob
        head_x = 51 if laying else 53
        head_y = 26 if laying else 12 + bob
        leg_offset = 0 if t % 2 == 0 else 2

        self.rect(25, 55, 33, 1, "#171819")

        if laying:
            self.rect(21, body_y + 6, 42, 14, outline)
            self.rect(25, body_y + 4, 34, 13, charcoal)
            self.rect(32, body_y + 5, 20, 4, shine)
            self.rect(29, body_y + 11, 13, 3, brindle)
            self.rect(24, body_y + 17, 18, 4, black)
            self.rect(43, body_y + 17, 18, 4, black)
        else:
            self.rect(19, body_y + 4, 43, 20, outline)
            self.rect(23, body_y + 2, 34, 20, charcoal)
            self.rect(30, body_y, 24, 7, shine)
            self.rect(56, body_y + 7, 8, 12, outline)
            self.rect(57, body_y + 8, 6, 10, charcoal)
            self.rect(33, body_y + 7, 18, 4, brindle)
            self.rect(41, body_y + 11, 11, 4, brindle_light)
            self.rect(25, body_y + 13, 29, 4, shadow)

            self.rect(25, 44 + leg_offset, 7, 10 - leg_offset, outline)
            self.rect(27, 43 + leg_offset, 5, 10 - leg_offset, black)
            self.rect(39, 43 - leg_offset, 7, 11 + leg_offset, outline)
            self.rect(41, 42 - leg_offset, 5, 11 + leg_offset, black)
            self.rect(54, 43 + leg_offset, 7, 11 - leg_offset, outline)
            self.rect(56, 42 + leg_offset, 5, 11 - leg_offset, black)
            self.rect(23, 53, 10, 4, warm_grey)
            self.rect(39, 53, 10, 4, warm_grey)
            self.rect(54, 53, 10, 4, warm_grey)

        tail_y = body_y + 2 + wag
        self.rect(7, tail_y + 8, 20, 5, outline)
        self.rect(3, tail_y + 4, 14, 6, outline)
        self.rect(5, tail_y, 10, 6, outline)
        self.rect(9, tail_y + 9, 17, 3, charcoal)
        self.rect(5, tail_y + 5, 12, 3, charcoal)
        self.rect(7, tail_y + 1, 7, 3, warm_grey)

        self.rect(head_x - 2, head_y + 1, 21, 18, outline)
        self.rect(head_x, head_y, 18, 17, charcoal)
        self.rect(head_x + 3, head_y - 4, 12, 7, outline)
        self.rect(head_x + 4, head_y - 5, 10, 6, shine)
        self.rect(head_x + 1, head_y + 3, 5, 7, "#303030")
        self.rect(head_x + 8, head_y + 8, 10, 8, grey)
        self.rect(head_x + 11, head_y + 11, 7, 5, warm_grey)
        self.rect(head_x + 9, head_y + 10, 3, 3, "#8a867f")
        self.rect(head_x + 14, head_y + 12, 3, 2, "#0d0d0d")

        self.rect(head_x - 4, head_y + 3, 6, 11, outline)
        self.rect(head_x - 3, head_y + 4, 4, 9, black)
        self.rect(head_x - 2, head_y + 6, 2, 5, "#2a2a2a")
        self.rect(head_x + 15, head_y + 2, 5, 12, outline)
        self.rect(head_x + 16, head_y + 3, 3, 10, black)
        self.rect(head_x + 16, head_y + 5, 2, 5, "#2a2a2a")

        if laying:
            self.rect(head_x + 10, head_y + 6, 4, 1, eye)
            self.rect(70, 16 - pant, 4, 2, "#d8d4cc")
            self.rect(77, 12 - pant, 3, 1, "#d8d4cc")
        else:
            self.rect(head_x + 6, head_y + 6, 1, 1, "#211b17")
            self.rect(head_x + 11, head_y + 5, 3, 3, eye)
            self.rect(head_x + 12, head_y + 5, 1, 1, eye_glint)
            self.rect(head_x + 15, head_y + 15, 3, 3 + pant * 2, tongue)

        if self.pose in {"happy", "trot", "patrol"}:
            self.rect(35, body_y + 7, 22, 7, amber)
            self.rect(51, body_y + 7, 6, 7, amber_shadow)
            self.rect(39, body_y + 10, 11, 2, "#f1cf67")
            self.rect(33, body_y + 6, 4, 9, "#704a25")

        if self.item == "leash":
            self.rect(61, 43, 12, 2, "#8b5a3d")
            self.rect(72, 40, 5, 5, "#8b5a3d")

    def draw_sprite_frame(self):
        pose = self.pose if self.pose in self.sprite_frames else "trot"
        if self.direction == -1 and f"{pose}_left" in self.sprite_frames:
            pose = f"{pose}_left"
        frames = self.sprite_frames.get(pose)
        if not frames:
            return False
        self.canvas.delete("all")
        self.canvas.create_image(2, 2, image=frames[0], anchor="nw")
        return True

    def tick(self):
        now = time.time()
        self.choose_pose(now)
        self.move(now)
        self.draw(now)
        self.root.after(33, self.tick)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    DexDesktop().run()
