import time
import traceback

from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button


class MacroPlayer:
    """Play recorded mouse/keyboard actions with interruptible timing."""

    def __init__(self, root, on_status=None, on_checkpoint=None, on_action=None):
        self.root = root
        self.on_status = on_status
        self.on_checkpoint = on_checkpoint
        self.on_action = on_action

        self.playing = False
        self.last_run_completed = False

        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(self, text, color="#aaaaaa"):
        if self.on_status:
            self.root.after(
                0,
                lambda: self.on_status(text, color)
            )

    # ========================================================
    # CHECKPOINT
    # ========================================================

    def show_checkpoint(self, screenshot):
        if not self.on_checkpoint:
            return

        self.root.after(
            0,
            lambda: self.on_checkpoint(screenshot)
        )

    # ========================================================
    # INTERRUPTIBLE WAIT
    # ========================================================

    def wait(self, duration):
        """Wait while still allowing ESC/Stop to interrupt playback."""

        end_time = time.monotonic() + max(0.0, duration)

        while self.playing:
            remaining = end_time - time.monotonic()

            if remaining <= 0:
                break

            time.sleep(min(remaining, 0.01))

    # ========================================================
    # PLAY
    # ========================================================

    def play(self, macro, repeat_count=1):

        if self.playing:
            return

        self.playing = True
        self.last_run_completed = False

        # ----------------------------------------------------
        # VALIDATE REPETITIONS
        # ----------------------------------------------------

        try:
            repeat_count = int(repeat_count)
        except (TypeError, ValueError):
            repeat_count = 1

        if repeat_count < 0:
            repeat_count = 1

        infinite = repeat_count == 0

        # ----------------------------------------------------
        # LOAD EVENTS
        # ----------------------------------------------------

        actions = sorted(
            macro.get("actions", []),
            key=lambda item: float(
                item.get("time", 0)
            )
        )

        screenshots = sorted(
            macro.get("screenshots", []),
            key=lambda item: float(
                item.get("time", 0)
            )
        )

        completed = False
        repetition = 0

        self.set_status(
            f"▶ Lecture : {macro['name']}",
            "#42a5f5"
        )

        print()
        print("=" * 60)
        print(f"[PLAY] Starting macro: {macro['name']}")
        print(f"[PLAY] Actions: {len(actions)}")
        print(f"[PLAY] Checkpoints: {len(screenshots)}")

        if infinite:
            print("[PLAY] Repetitions: INFINITE")
        else:
            print(f"[PLAY] Repetitions: {repeat_count}")

        print("=" * 60)

        try:

            # ====================================================
            # REPETITION LOOP
            # ====================================================

            while self.playing:

                # Stop after the requested number of repetitions.
                if not infinite and repetition >= repeat_count:
                    completed = True
                    break

                repetition += 1

                if infinite:
                    repetition_text = f"{repetition} / ∞"
                else:
                    repetition_text = (
                        f"{repetition} / {repeat_count}"
                    )

                print()
                print(
                    f"[PLAY] Starting repetition "
                    f"{repetition_text}"
                )

                self.set_status(
                    f"▶ Lecture : {macro['name']} "
                    f"— {repetition_text}",
                    "#42a5f5"
                )

                # ------------------------------------------------
                # RESET TIMING FOR THIS REPETITION
                # ------------------------------------------------

                action_index = 0
                screenshot_index = 0
                current_time = 0.0

                # ------------------------------------------------
                # PLAY THIS REPETITION
                # ------------------------------------------------

                while self.playing:

                    # --------------------------------------------
                    # NEXT ACTION TIME
                    # --------------------------------------------

                    if action_index < len(actions):

                        next_action_time = float(
                            actions[action_index].get(
                                "time",
                                0
                            )
                        )

                    else:

                        next_action_time = float("inf")

                    # --------------------------------------------
                    # NEXT SCREENSHOT TIME
                    # --------------------------------------------

                    if screenshot_index < len(screenshots):

                        next_screenshot_time = float(
                            screenshots[screenshot_index].get(
                                "time",
                                0
                            )
                        )

                    else:

                        next_screenshot_time = float("inf")

                    # --------------------------------------------
                    # NEXT EVENT
                    # --------------------------------------------

                    next_time = min(
                        next_action_time,
                        next_screenshot_time
                    )

                    # No more events for this repetition.
                    if next_time == float("inf"):
                        break

                    # --------------------------------------------
                    # WAIT
                    # --------------------------------------------

                    delay = next_time - current_time

                    if delay > 0:
                        self.wait(delay)

                    if not self.playing:
                        break

                    current_time = next_time

                    # --------------------------------------------
                    # CHECKPOINTS
                    # --------------------------------------------

                    while (
                        self.playing
                        and screenshot_index < len(screenshots)
                    ):

                        screenshot = screenshots[
                            screenshot_index
                        ]

                        screenshot_time = float(
                            screenshot.get(
                                "time",
                                0
                            )
                        )

                        if screenshot_time > current_time + 0.0001:
                            break

                        # print(
                        #     "[CHECKPOINT] "
                        #     f"{screenshot.get("
                        #         "name",
                        #         screenshot.get(
                        #             "description",
                        #             "Checkpoint"
                        #         )
                        #     )} "
                        #     f"@ "
                        #     f"{screenshot_time:.3f}s"
                        # )

                        self.show_checkpoint(
                            screenshot
                        )

                        screenshot_index += 1

                    # --------------------------------------------
                    # ACTIONS
                    # --------------------------------------------

                    while (
                        self.playing
                        and action_index < len(actions)
                    ):

                        action = actions[
                            action_index
                        ]

                        action_time = float(
                            action.get(
                                "time",
                                0
                            )
                        )

                        if action_time > current_time + 0.0001:
                            break

                        print(
                            "[PLAY] Action "
                            f"{action_index + 1}/"
                            f"{len(actions)} "
                            f"{action.get('type')} "
                            f"@ "
                            f"{action_time:.3f}s"
                        )

                        if self.on_action:
                            self.root.after(0, lambda item=action: self.on_action(item))

                        self.execute_action(
                            action
                        )

                        action_index += 1

                    # --------------------------------------------
                    # REPETITION FINISHED
                    # --------------------------------------------

                    if (
                        action_index >= len(actions)
                        and screenshot_index >= len(screenshots)
                    ):
                        break

                # ------------------------------------------------
                # STOP CHECK
                # ------------------------------------------------

                if not self.playing:
                    print(
                        f"[PLAY] STOP DÉTECTÉ après la répétition "
                        f"{repetition}"
                    )
                    break

                print(
                    f"[PLAY] FIN REPETITION {repetition}"
                )
                print(
                    f"[PLAY] playing = {self.playing}"
                )
                print(
                    f"[PLAY] action_index = {action_index}/{len(actions)}"
                )
                print(
                    f"[PLAY] screenshot_index = "
                    f"{screenshot_index}/{len(screenshots)}"
                )
                print(
                    f"[PLAY] Repetition "
                    f"{repetition_text} completed"
                )

                # The outer while loop now starts the next
                # repetition automatically.

            # ====================================================
            # COMPLETION
            # ====================================================

            if self.playing:
                completed = True

        except Exception as exc:

            print()
            print(
                f"[PLAY] Fatal playback error: {exc}"
            )

            traceback.print_exc()

            self.set_status(
                f"❌ Erreur de lecture : {exc}",
                "#f44336"
            )

            completed = False

        finally:

            self.playing = False

            print("=" * 60)

            self.last_run_completed = completed

            if completed:

                print("[PLAY] Completed")

                self.set_status(
                    "● Prêt",
                    "#aaaaaa"
                )

            else:

                print("[PLAY] Stopped")

                self.set_status(
                    "● Lecture arrêtée",
                    "#ff9800"
                )

            print("=" * 60)
            print()

    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        print("=" * 60)
        print(f"[PLAY] stop() appelé ! playing={self.playing}")
        print("=" * 60)

        if self.playing:

            self.playing = False

            self.set_status(
                "■ Arrêt demandé...",
                "#ff9800"
            )

    # ========================================================
    # MOUSE BUTTON
    # ========================================================

    @staticmethod
    def get_mouse_button(button_name):
        """Convert the recorded button name to a Button object."""

        if isinstance(button_name, Button):
            return button_name

        if not isinstance(button_name, str):
            raise ValueError(
                f"Invalid mouse button: {button_name!r}"
            )

        name = button_name.lower().strip()

        if name in (
            "button.left",
            "left"
        ):
            return Button.left

        if name in (
            "button.right",
            "right"
        ):
            return Button.right

        if name in (
            "button.middle",
            "middle"
        ):
            return Button.middle

        raise ValueError(
            f"Unknown mouse button: {button_name!r}"
        )

    # ========================================================
    # MOUSE CLICK
    # ========================================================

    def execute_mouse_click(self, data):

        if not isinstance(data, dict):
            raise ValueError(
                f"Invalid mouse_click data: {data!r}"
            )

        x = int(data["x"])
        y = int(data["y"])

        button_name = data.get(
            "button",
            "Button.left"
        )

        button = self.get_mouse_button(
            button_name
        )

        print(
            "[MOUSE] Requested click: "
            f"x={x}, y={y}, "
            f"button={button_name}"
        )

        # ----------------------------------------------------
        # MOVE
        # ----------------------------------------------------

        self.mouse.position = (
            x,
            y
        )

        print(
            "[MOUSE] Position after move: "
            f"{self.mouse.position}"
        )

        time.sleep(0.01)

        # ----------------------------------------------------
        # VERIFY POSITION
        # ----------------------------------------------------

        actual_x, actual_y = self.mouse.position

        if (
            abs(actual_x - x) > 2
            or abs(actual_y - y) > 2
        ):
            raise RuntimeError(
                "Mouse position mismatch: "
                f"requested=({x}, {y}), "
                f"actual=({actual_x}, {actual_y})"
            )

        # ----------------------------------------------------
        # CLICK
        # ----------------------------------------------------

        print(
            "[MOUSE] Sending click: "
            f"{button} at "
            f"({actual_x}, {actual_y})"
        )

        self.mouse.click(
            button,
            1
        )

        print(
            "[MOUSE] Click sent successfully"
        )

    # ========================================================
    # ACTION
    # ========================================================

    def execute_action(self, action):

        action_type = action.get("type")
        data = action.get("data")

        action_time = float(
            action.get(
                "time",
                0
            )
        )

        try:

            # =================================================
            # KEYBOARD
            # =================================================

            if action_type == "key_press":

                if data is None:

                    self.set_status(
                        f"⚠ Touche ignorée à "
                        f"{action_time:.2f}s : data=None",
                        "#ff9800"
                    )

                    print(
                        "[KEY] Ignored: data=None "
                        f"@ {action_time:.3f}s"
                    )

                    return

                # Les touches spéciales enregistrées sont stockées sous forme
                # de texte, par exemple "Key.page_up". pynput attend un objet Key.
                key_to_press = data
                if isinstance(data, str) and data.startswith("Key."):
                    key_name = data.split(".", 1)[1]
                    key_to_press = getattr(Key, key_name, None)
                    if key_to_press is None:
                        raise ValueError(f"Touche spéciale inconnue : {data}")

                print(
                    f"[KEY] Press: {data!r}"
                )

                self.keyboard.press(key_to_press)
                self.keyboard.release(key_to_press)

                self.set_status(
                    f"⌨ {data} "
                    f"({action_time:.2f}s)",
                    "#aaaaaa"
                )

            # =================================================
            # MOUSE CLICK
            # =================================================

            elif action_type == "mouse_click":

                self.execute_mouse_click(
                    data
                )

                self.set_status(
                    f"🖱 Clic "
                    f"({data['x']}, {data['y']}) "
                    f"à {action_time:.2f}s",
                    "#aaaaaa"
                )

            # =================================================
            # MOUSE SCROLL
            # =================================================

            elif action_type == "mouse_scroll":

                if not isinstance(data, dict):
                    raise ValueError(
                        f"Invalid mouse_scroll data: {data!r}"
                    )

                x = int(
                    data["x"]
                )

                y = int(
                    data["y"]
                )

                dx = int(
                    data.get(
                        "dx",
                        0
                    )
                )

                dy = int(
                    data.get(
                        "dy",
                        0
                    )
                )

                print(
                    "[MOUSE] Scroll: "
                    f"position=({x}, {y}), "
                    f"dx={dx}, dy={dy}"
                )

                self.mouse.position = (
                    x,
                    y
                )

                self.mouse.scroll(
                    dx,
                    dy
                )

                self.set_status(
                    f"🖱 Scroll "
                    f"({x}, {y}) "
                    f"à {action_time:.2f}s",
                    "#aaaaaa"
                )

            # =================================================
            # UNKNOWN
            # =================================================

            else:

                raise ValueError(
                    f"Unknown action type: "
                    f"{action_type!r}"
                )

        except Exception as exc:

            message = (
                f"❌ ERREUR ACTION "
                f"{action_time:.2f}s "
                f"({action_type}): {exc}"
            )

            print()
            print("=" * 60)
            print(message)
            print(f"[PLAY] playing AVANT arrêt : {self.playing}")
            traceback.print_exc()
            print("=" * 60)

            self.set_status(
                message,
                "#f44336"
            )

            self.playing = False