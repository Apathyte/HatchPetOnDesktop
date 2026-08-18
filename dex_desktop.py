import ctypes
from ctypes import wintypes
import math
import os
import random
import sys
import time
import tkinter as tk


TRANSPARENT = "#ff00ff"
SCALE = 2
PET_W = 188
PET_H = 170
SPRITE_Y = PET_H - 132 + 2
DEX_VERSION = "v11-walk-cleanup-backlog"


class WindowsActivityMonitor:
    def __init__(self):
        self.enabled = sys.platform.startswith("win")
        self.last_cpu = None
        self.current_app = None
        self.current_app_since = time.time()
        if not self.enabled:
            return

        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    def snapshot(self):
        if not self.enabled:
            return {"exe": "", "title": "", "cpu": None, "active_seconds": 0}

        exe, title = self.foreground_app()
        cpu = self.cpu_percent()
        key = (exe.lower(), title)
        now = time.time()
        if key != self.current_app:
            self.current_app = key
            self.current_app_since = now

        return {
            "exe": exe.lower(),
            "title": title.lower(),
            "cpu": cpu,
            "active_seconds": now - self.current_app_since,
        }

    def foreground_app(self):
        hwnd = self.user32.GetForegroundWindow()
        if not hwnd:
            return "", ""

        title_len = self.user32.GetWindowTextLengthW(hwnd)
        title_buf = ctypes.create_unicode_buffer(title_len + 1)
        self.user32.GetWindowTextW(hwnd, title_buf, title_len + 1)

        pid = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        exe = self.process_name(pid.value)
        return exe, title_buf.value

    def process_name(self, pid):
        if not pid:
            return ""
        handle = self.kernel32.OpenProcess(self.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return ""
        try:
            buf = ctypes.create_unicode_buffer(512)
            size = wintypes.DWORD(len(buf))
            ok = self.kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size))
            if not ok:
                return ""
            return os.path.basename(buf.value)
        finally:
            self.kernel32.CloseHandle(handle)

    def cpu_percent(self):
        idle = wintypes.FILETIME()
        kernel = wintypes.FILETIME()
        user = wintypes.FILETIME()
        if not self.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
            return None

        def filetime_to_int(ft):
            return (ft.dwHighDateTime << 32) + ft.dwLowDateTime

        current = (filetime_to_int(idle), filetime_to_int(kernel), filetime_to_int(user))
        if self.last_cpu is None:
            self.last_cpu = current
            return None

        idle_delta = current[0] - self.last_cpu[0]
        kernel_delta = current[1] - self.last_cpu[1]
        user_delta = current[2] - self.last_cpu[2]
        total = kernel_delta + user_delta
        self.last_cpu = current
        if total <= 0:
            return None
        return max(0, min(100, (total - idle_delta) * 100 / total))


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
        self.step_phase = 0.0
        self.stride_clock = 0.0
        self.mode = "roaming"
        self.manual_until = 0
        self.always_on_top = True
        self.activity_monitor = WindowsActivityMonitor()
        self.current_reaction = "none"
        self.current_activity = {"exe": "", "title": "", "cpu": None, "active_seconds": 0}
        self.status_window = None
        self.status_value_labels = {}
        self.test_reaction = None

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.canvas.bind("<Button-3>", self.show_menu)

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Give attention", command=self.give_attention)
        self.menu.add_command(label="Walk Dex", command=self.walk)
        self.menu.add_command(label="Zoomies", command=self.zoomies)
        self.menu.add_separator()
        self.menu.add_command(label="Nap", command=self.nap)
        self.menu.add_command(label="Wake up", command=self.wake_up)
        self.menu.add_command(label="Patrol", command=self.start_patrol)
        self.menu.add_command(label="Drop leash", command=self.drop_leash)
        self.menu.add_command(label="Sit / stay", command=self.sit_stay)
        self.menu.add_command(label="Resume roaming", command=self.resume_roaming)
        self.menu.add_separator()
        self.menu.add_command(label="Reset position", command=self.reset_position)
        self.always_menu_index = self.menu.index("end") + 1
        self.menu.add_command(label="Always on top: yes", command=self.toggle_always_on_top)
        self.pause_menu_index = self.menu.index("end") + 1
        self.menu.add_command(label="Pause roaming", command=self.toggle_pause_roaming)
        self.menu.add_command(label="Show status", command=self.show_status)
        self.menu.add_cascade(label="Test reactions", menu=self.build_test_reaction_menu())
        self.menu.add_separator()
        self.menu.add_command(label="Exit Dex", command=self.root.destroy)

        self.root.geometry(f"{PET_W}x{PET_H}+{self.x}+{self.y}")
        self.sprite_frames = self.load_sprite_frames()
        self.overlay_frames = self.load_overlay_frames()
        self.tick()

    def load_sprite_frames(self):
        base = os.path.join(os.path.dirname(__file__), "assets", "dex-concept")
        frames = {}
        for pose in ("trot", "happy", "patrol", "sleep", "leash", "sit", "zoom"):
            pose_frames = []
            left_frames = []
            i = 0
            while True:
                path = os.path.join(base, f"{pose}_{i}.png")
                left_path = os.path.join(base, f"{pose}_{i}_left.png")
                if not os.path.exists(path):
                    break
                pose_frames.append(tk.PhotoImage(file=path))
                if os.path.exists(left_path):
                    left_frames.append(tk.PhotoImage(file=left_path))
                i += 1
            if pose_frames:
                frames[pose] = pose_frames
            if left_frames:
                frames[f"{pose}_left"] = left_frames
        return frames

    def load_overlay_frames(self):
        base = os.path.join(os.path.dirname(__file__), "assets", "dex-overlays")
        overlays = {}
        for name in ("excel_brow", "excel_sigh", "excel_sigh_0", "excel_sigh_1", "excel_sigh_2"):
            path = os.path.join(base, f"{name}.png")
            left_path = os.path.join(base, f"{name}_left.png")
            if os.path.exists(path):
                overlays[name] = tk.PhotoImage(file=path)
            if os.path.exists(left_path):
                overlays[f"{name}_left"] = tk.PhotoImage(file=left_path)
        return overlays

    def build_test_reaction_menu(self):
        menu = tk.Menu(self.menu, tearoff=0)
        menu.add_command(label="Test Excel reaction", command=lambda: self.set_test_reaction("excel_disappointed"))
        menu.add_command(label="Test PowerPoint reaction", command=lambda: self.set_test_reaction("powerpoint_bored"))
        menu.add_command(label="Test Meeting fatigue", command=lambda: self.set_test_reaction("meeting_fatigue"))
        menu.add_command(label="Test Engineering supervision", command=lambda: self.set_test_reaction("supervising"))
        menu.add_separator()
        menu.add_command(label="Clear test reaction", command=self.clear_test_reaction)
        return menu

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
        self.refresh_menu_labels()
        self.menu.tk_popup(event.x_root, event.y_root)

    def give_attention(self):
        self.set_mode("happy", duration=10)
        self.attention_until = time.time() + 10
        self.sleep_after = time.time() + 35 * 60

    def walk(self):
        self.set_mode("happy", duration=16)
        self.last_walk = time.time()
        self.attention_until = time.time() + 16
        self.sleep_after = time.time() + 35 * 60

    def zoomies(self):
        self.set_mode("zoomies", duration=4)
        self.zoomies_until = time.time() + 4

    def set_mode(self, mode, duration=None):
        self.mode = mode
        self.manual_until = time.time() + duration if duration is not None else None

    def clear_expired_manual_mode(self, now):
        if self.manual_until and now >= self.manual_until:
            self.resume_roaming()

    def resume_roaming(self):
        self.mode = "roaming"
        self.manual_until = 0
        self.attention_until = 0
        self.zoomies_until = 0

    def nap(self):
        self.set_mode("sleeping")

    def wake_up(self):
        self.sleep_after = time.time() + 35 * 60
        self.last_walk = time.time()
        self.set_mode("happy", duration=8)

    def start_patrol(self):
        self.set_mode("patrol")

    def drop_leash(self):
        self.set_mode("leash")

    def sit_stay(self):
        self.set_mode("sit_stay")

    def pause_roaming(self):
        self.set_mode("paused")

    def toggle_pause_roaming(self):
        if self.mode == "paused":
            self.resume_roaming()
        else:
            self.pause_roaming()

    def reset_position(self):
        self.x = max(8, min(self.screen_w - PET_W - 8, self.screen_w // 2 - PET_W // 2))
        self.y = self.screen_h - PET_H - 54
        self.direction = 1
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    def toggle_always_on_top(self):
        self.always_on_top = not self.always_on_top
        self.root.attributes("-topmost", self.always_on_top)
        self.refresh_menu_labels()

    def set_test_reaction(self, reaction):
        self.test_reaction = reaction
        self.resume_roaming()

    def clear_test_reaction(self):
        self.test_reaction = None
        self.resume_roaming()

    def refresh_menu_labels(self):
        top_label = "Always on top: yes" if self.always_on_top else "Always on top: no"
        pause_label = "Resume roaming" if self.mode == "paused" else "Pause roaming"
        self.menu.entryconfig(self.always_menu_index, label=top_label)
        self.menu.entryconfig(self.pause_menu_index, label=pause_label)

    def show_status(self):
        if self.status_window is not None and self.status_window.winfo_exists():
            self.status_window.lift()
            self.refresh_status_window()
            return

        self.status_window = tk.Toplevel(self.root)
        self.status_window.title("Dex status")
        self.status_window.attributes("-topmost", self.always_on_top)
        self.status_window.resizable(False, False)
        self.status_window.configure(bg="#232323")
        self.status_window.protocol("WM_DELETE_WINDOW", self.close_status_window)
        self.status_value_labels = {}

        labels = ["Mode", "Pose", "Reaction", "Test reaction", "Detected app", "Window title", "Active time", "CPU", "Always on top"]

        for row, label in enumerate(labels):
            tk.Label(self.status_window, text=label, anchor="w", bg="#232323", fg="#c7c1b6", padx=10, pady=3).grid(row=row, column=0, sticky="w")
            value_label = tk.Label(self.status_window, text="", anchor="w", bg="#232323", fg="#f2eadc", padx=10, pady=3)
            value_label.grid(row=row, column=1, sticky="w")
            self.status_value_labels[label] = value_label

        tk.Button(self.status_window, text="Close", command=self.close_status_window).grid(row=len(labels), column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.refresh_status_window()

    def close_status_window(self):
        if self.status_window is not None and self.status_window.winfo_exists():
            self.status_window.destroy()
        self.status_window = None
        self.status_value_labels = {}

    def refresh_status_window(self):
        if self.status_window is None:
            return
        try:
            if not self.status_window.winfo_exists():
                self.close_status_window()
                return
        except tk.TclError:
            self.status_window = None
            self.status_value_labels = {}
            return

        activity = self.current_activity
        cpu = activity.get("cpu")
        title = activity.get("title") or ""
        if len(title) > 72:
            title = title[:69] + "..."

        values = {
            "Mode": self.mode,
            "Pose": self.pose,
            "Reaction": self.current_reaction,
            "Test reaction": self.test_reaction or "none",
            "Detected app": activity.get("exe") or "unknown",
            "Window title": title or "unknown",
            "Active time": f"{int(activity.get('active_seconds') or 0)}s",
            "CPU": "unknown" if cpu is None else f"{cpu:.0f}%",
            "Always on top": "yes" if self.always_on_top else "no",
        }

        for label, value in values.items():
            widget = self.status_value_labels.get(label)
            if widget is not None:
                widget.config(text=value)

        self.status_window.after(500, self.refresh_status_window)

    def choose_pose(self, now):
        self.current_activity = self.activity_monitor.snapshot()
        self.clear_expired_manual_mode(now)
        inactive = now - self.last_walk
        self.pose = "trot"
        self.item = "none"
        self.gear = "none"
        self.current_reaction = "none"

        if self.mode == "happy":
            self.pose = "happy"
            return

        if self.mode == "sleeping":
            self.pose = "sleep"
            return

        if self.mode == "leash":
            self.pose = "leash"
            self.item = "leash"
            return

        if self.mode == "patrol":
            self.pose = "patrol"
            return

        if self.mode == "zoomies":
            self.pose = "zoom"
            return

        if self.mode == "sit_stay":
            self.pose = "sit"
            return

        if self.mode == "paused":
            self.pose = "trot"
            return

        if self.apply_activity_reaction():
            return

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

    def apply_activity_reaction(self):
        if self.apply_named_reaction(self.test_reaction, is_test=True):
            return True

        activity = self.current_activity
        exe = activity["exe"]
        title = activity["title"]
        active_seconds = activity["active_seconds"]
        cpu = activity["cpu"]

        if cpu is not None and cpu >= 85:
            self.apply_named_reaction("cpu_spike")
            return True

        if exe == "excel.exe":
            self.apply_named_reaction("excel_disappointed")
            return True

        if exe == "powerpnt.exe":
            self.apply_named_reaction("powerpoint_bored_long" if active_seconds >= 20 * 60 else "powerpoint_bored")
            return True

        if exe in {"teams.exe", "ms-teams.exe", "zoom.exe"}:
            self.apply_named_reaction("meeting_fatigue" if active_seconds >= 60 * 60 else "meeting_watch")
            return True

        engineering_exes = {
            "code.exe",
            "windowsterminal.exe",
            "powershell.exe",
            "pwsh.exe",
            "cmd.exe",
            "docker desktop.exe",
        }
        engineering_titles = ("node-red", "ignition", "gateway", "docker", "plc")
        if exe in engineering_exes or any(token in title for token in engineering_titles):
            self.apply_named_reaction("supervising")
            return True

        return False

    def apply_named_reaction(self, reaction, is_test=False):
        if not reaction:
            return False

        self.current_reaction = f"test_{reaction}" if is_test else reaction

        if reaction == "excel_disappointed":
            self.pose = "sit"
            return True

        if reaction == "powerpoint_bored":
            self.pose = "sit"
            return True

        if reaction == "powerpoint_bored_long":
            self.pose = "sleep"
            return True

        if reaction in {"meeting_watch", "meeting_fatigue"}:
            if reaction == "meeting_fatigue":
                self.pose = "leash"
                self.item = "leash"
            else:
                self.pose = "sit"
            return True

        if reaction in {"supervising", "cpu_spike"}:
            self.pose = "patrol"
            return True

        return False

    def move(self, now):
        if self.dragging:
            return

        floor_y = self.screen_h - PET_H - 54
        self.y = floor_y + 12 if self.pose == "sleep" else floor_y

        if self.mode in {"paused", "sit_stay", "leash"} or self.pose == "sit":
            speed = 0
        elif self.pose == "sleep":
            speed = 0
        elif self.pose == "zoom":
            speed = 10
        elif self.pose == "patrol":
            speed = 1.25
        elif self.pose == "leash":
            speed = 0.55
        else:
            speed = 0.42

        if self.pose == "leash" and self.mode != "leash":
            target_x = 24 if self.x < self.screen_w / 2 else self.screen_w - PET_W - 24
            delta = (target_x - self.x) * 0.018
            self.x += self.grounded_stride(delta, now)
        else:
            self.x += self.grounded_stride(speed * self.direction, now)

        if self.x < 8:
            self.x = 8
            self.direction = 1
        elif self.x > self.screen_w - PET_W - 8:
            self.x = self.screen_w - PET_W - 8
            self.direction = -1

        if random.random() < 0.0009 and self.pose == "trot":
            self.zoomies()

        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    def grounded_stride(self, desired_delta, now):
        if abs(desired_delta) < 0.01:
            self.step_phase = 0.0
            return 0

        rate = 13 if self.pose == "zoom" else 7 if self.pose in {"happy", "trot"} else 4
        self.stride_clock = now * rate
        phase = (math.sin(self.stride_clock) + 1) / 2
        planted = phase < 0.34
        self.step_phase = phase
        if planted and self.pose != "zoom":
            return desired_delta * 0.18
        return desired_delta * (1.55 if self.pose != "zoom" else 1.1)

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
        if self.direction == 1 and f"{pose}_left" in self.sprite_frames:
            pose = f"{pose}_left"
        frames = self.sprite_frames.get(pose)
        if not frames:
            return False
        self.canvas.delete("all")
        stride = 0
        if self.pose in {"trot", "happy", "patrol", "leash", "zoom"}:
            stride = -1 if self.step_phase < 0.5 else 1
        rate = 14 if pose.startswith("zoom") else 7 if pose.startswith(("trot", "happy", "patrol")) else 3
        index = int(time.time() * rate) % len(frames)
        sprite_x = 2 + stride
        self.canvas.create_image(sprite_x, SPRITE_Y, image=frames[index], anchor="nw")
        self.draw_reaction_overlays(pose, sprite_x, SPRITE_Y)
        self.draw_life_overlays(pose, SPRITE_Y)
        return True

    def draw_reaction_overlays(self, pose, x, y):
        if not self.current_reaction.endswith("excel_disappointed"):
            return

        self.draw_growl_balloon(pose, x, y)

    def draw_growl_balloon(self, pose, x, y):
        facing_right = pose.endswith("_left")
        pulse = 1 if int(time.time() * 3) % 2 else 0

        if facing_right:
            bubble = (18, 4 + pulse, 92, 30 + pulse)
            tail = [(82, 27 + pulse), (103, 42 + pulse), (91, 20 + pulse)]
            text_x = 55
        else:
            bubble = (96, 4 + pulse, 178, 30 + pulse)
            tail = [(108, 27 + pulse), (85, 42 + pulse), (99, 20 + pulse)]
            text_x = 137

        self.canvas.create_oval(*bubble, fill="#fff6d8", outline="#31271f", width=2)
        self.canvas.create_polygon(tail, fill="#fff6d8", outline="#31271f", width=2)
        self.canvas.create_text(
            text_x,
            17 + pulse,
            text="GRROWWLL",
            fill="#31271f",
            font=("TkDefaultFont", 8, "bold"),
        )

    def draw_life_overlays(self, pose, sprite_y):
        now = time.time()
        facing_right = pose.endswith("_left")
        blink = now % 6.5 > 6.25

        if facing_right:
            eye_box = (133, sprite_y + 33, 141, sprite_y + 37)
        else:
            eye_box = (45, sprite_y + 33, 53, sprite_y + 37)

        if blink and self.pose not in {"sleep"}:
            self.canvas.create_rectangle(*eye_box, fill="#1b1b1b", outline="#1b1b1b")

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
