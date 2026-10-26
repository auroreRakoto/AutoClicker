import time

from pynput import keyboard, mouse


class Recorder:
    """
    Gère l'enregistrement des actions clavier et souris.
    """

    def __init__(self, on_status=None):
        self.on_status = on_status

        self.recording = False
        self.paused = False

        self.actions = []

        self.record_start_time = 0
        self.pause_start_time = None
        self.total_pause_time = 0

        self.keyboard_listener = None
        self.mouse_listener = None

        self.on_stop_callback = None
        self.on_screenshot_callback = None

    # ========================================================
    # CALLBACKS
    # ========================================================

    def set_stop_callback(self, callback):
        self.on_stop_callback = callback

    def set_screenshot_callback(self, callback):
        self.on_screenshot_callback = callback

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(self, text, color="#aaaaaa"):
        if self.on_status:
            self.on_status(text, color)

    # ========================================================
    # TEMPS
    # ========================================================

    def get_elapsed_time(self):
        if not self.recording:
            return 0

        elapsed = time.time() - self.record_start_time

        pause_time = self.total_pause_time

        if self.paused and self.pause_start_time:
            pause_time += time.time() - self.pause_start_time

        return max(
            0,
            elapsed - pause_time
        )

    # ========================================================
    # AJOUT ACTION
    # ========================================================

    def add_action(self, action_type, data):
        if not self.recording:
            return

        if self.paused:
            return

        self.actions.append({
            "type": action_type,
            "data": data,
            "time": self.get_elapsed_time()
        })

    # ========================================================
    # CLAVIER
    # ========================================================

    def on_key_press(self, key):
        if not self.recording:
            return

        if self.paused:
            return

        # ESC est réservé à l'arrêt de lecture.
        if key == keyboard.Key.esc:
            return

        try:
            value = key.char
        except AttributeError:
            value = str(key)

        # + est réservé au screenshot.
        if value == "+":
            return

        self.add_action(
            "key_press",
            value
        )

    # ========================================================
    # SOURIS
    # ========================================================

    def on_mouse_click(
        self,
        x,
        y,
        button,
        pressed
    ):
        if not self.recording:
            return

        if self.paused:
            return

        if not pressed:
            return

        self.add_action(
            "mouse_click",
            {
                "x": x,
                "y": y,
                "button": str(button)
            }
        )

    def on_mouse_scroll(
        self,
        x,
        y,
        dx,
        dy
    ):
        if not self.recording:
            return

        if self.paused:
            return

        self.add_action(
            "mouse_scroll",
            {
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy
            }
        )

    # ========================================================
    # DÉMARRER
    # ========================================================

    def start(self):
        if self.recording:
            return

        self.actions = []

        self.record_start_time = time.time()

        self.pause_start_time = None
        self.total_pause_time = 0

        self.recording = True
        self.paused = False

        self.set_status(
            "● Enregistrement en cours...",
            "#ff5252"
        )

    # ========================================================
    # PAUSE
    # ========================================================

    def pause(self):
        if not self.recording:
            return

        if self.paused:
            return

        self.paused = True
        self.pause_start_time = time.time()

    # ========================================================
    # REPRISE
    # ========================================================

    def resume(self):
        if not self.recording:
            return

        if not self.paused:
            return

        self.total_pause_time += (
            time.time() - self.pause_start_time
        )

        self.pause_start_time = None
        self.paused = False

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):
        if not self.recording:
            return

        if self.paused:
            self.total_pause_time += (
                time.time() - self.pause_start_time
            )

        self.recording = False
        self.paused = False

        self.pause_start_time = None

        self.set_status(
            f"● Enregistrement terminé — "
            f"{len(self.actions)} actions",
            "#4caf50"
        )

        if self.on_stop_callback:
            self.on_stop_callback(
                self.actions
            )

    # ========================================================
    # LISTENERS
    # ========================================================

    def start_listeners(self):
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )

        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )

        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop_listeners(self):
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        if self.mouse_listener:
            self.mouse_listener.stop()
