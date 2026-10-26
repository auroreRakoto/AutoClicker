"""Small always-on-top status overlay shared by AutoClicker and Script Runner."""
import time
import tkinter as tk


class StatusOverlay:
    def __init__(self, root, title="AutoClicker"):
        self.root = root
        self.started_at = None
        self.active = False
        self.window = tk.Toplevel(root)
        self.window.title(title)
        self.window.geometry("300x92+30+30")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.configure(bg="#202124")
        self.window.withdraw()
        self.message = tk.StringVar(value="Prêt")
        self.clock = tk.StringVar(value="00:00:00")
        tk.Label(self.window, textvariable=self.message, bg="#202124", fg="#8ab4f8",
                 font=("Segoe UI", 10, "bold"), anchor="w", wraplength=280).pack(
                     fill="x", padx=10, pady=(8, 2))
        tk.Label(self.window, textvariable=self.clock, bg="#202124", fg="white",
                 font=("Consolas", 16, "bold"), anchor="w").pack(fill="x", padx=10, pady=(0, 8))
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self._tick()

    def start(self, message):
        self.started_at = time.monotonic()
        self.active = True
        self.message.set(message)
        self.window.deiconify()
        self.window.lift()

    def update(self, message):
        if not self.active:
            self.start(message)
        else:
            self.message.set(message)

    def stop(self, message="Terminé"):
        self.message.set(message)
        self.active = False
        self.started_at = None
        self.clock.set("00:00:00")
        self.window.after(1800, self.hide)

    def hide(self):
        self.active = False
        try:
            self.window.withdraw()
        except tk.TclError:
            pass

    def _tick(self):
        if self.active and self.started_at is not None:
            elapsed = max(0, int(time.monotonic() - self.started_at))
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.clock.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        try:
            self.window.after(200, self._tick)
        except tk.TclError:
            pass

    def destroy(self):
        try:
            self.window.destroy()
        except tk.TclError:
            pass
