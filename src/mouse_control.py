# %% [markdown]
# ## 3. Mouse Controller
# Executes the confirmed gesture: smooth cursor movement, one-shot clicks, joystick-style scroll.

# %%
import math
import sys
import time

import numpy as np
import pyautogui

from gesture_recognizer import Gesture

pyautogui.FAILSAFE = True   # slam the physical mouse into a screen corner to abort
pyautogui.PAUSE = 0         # default is 0.1 s delay per call, which makes the cursor laggy

# Windows scroll units: 120 = one wheel notch. Mac/Linux use "lines".
MAX_SCROLL = 100 if sys.platform.startswith("win") else 10


class MouseController:
    def __init__(self, cam_w, cam_h, screen_w, screen_h,
                 margin=100, click_cooldown=0.35, scroll_deadzone=0.06):
        self.cam_w, self.cam_h = cam_w, cam_h
        self.screen_w, self.screen_h = screen_w, screen_h
        self.margin = margin                    # active-area border (px) so screen edges are reachable
        self.click_cooldown = click_cooldown
        self.scroll_deadzone = scroll_deadzone  # fraction of frame height where scroll does nothing

        self.prev_gesture = Gesture.NONE
        self.cursor = None                      # smoothed cursor position
        self.last_click = 0.0
        self.last_scroll = 0.0
        self.scroll_anchor = None               # y where the scroll gesture started

    # ---- main entry -----------------------------------------------------
    def update(self, gesture, point):
        """gesture: confirmed Gesture. point: (x, y) tracking point in camera pixels."""
        entering = gesture != self.prev_gesture

        if point is not None:
            if gesture == Gesture.MOVE:
                if entering:
                    self.cursor = tuple(pyautogui.position())  # resume from real cursor, no jump
                self._move(point)
            elif gesture in (Gesture.LEFT_CLICK, Gesture.RIGHT_CLICK) and entering:
                self._click(gesture)
            elif gesture == Gesture.SCROLL:
                self._scroll(point)

        if gesture != Gesture.SCROLL:
            self.scroll_anchor = None
        self.prev_gesture = gesture

    # ---- actions --------------------------------------------------------
    def _move(self, point):
        m = self.margin
        tx = np.interp(point[0], (m, self.cam_w - m), (0, self.screen_w))
        ty = np.interp(point[1], (m, self.cam_h - m), (0, self.screen_h))

        cx, cy = self.cursor
        dist = math.hypot(tx - cx, ty - cy)
        if dist < 6:                       # dead zone: ignore tiny hand jitter
            return
        # Adaptive smoothing: slow hand = heavy smoothing (precise), fast hand = responsive
        alpha = float(np.interp(dist, (6, 300), (0.12, 0.6)))
        cx += (tx - cx) * alpha
        cy += (ty - cy) * alpha

        # Stay 2 px away from the corners so our own cursor never triggers the failsafe
        cx = float(np.clip(cx, 2, self.screen_w - 3))
        cy = float(np.clip(cy, 2, self.screen_h - 3))
        self.cursor = (cx, cy)
        pyautogui.moveTo(cx, cy)

    def _click(self, gesture):
        now = time.time()
        if now - self.last_click < self.click_cooldown:
            return
        if gesture == Gesture.LEFT_CLICK:
            pyautogui.click()
        else:
            pyautogui.rightClick()
        self.last_click = now

    def _scroll(self, point):
        y = point[1]
        if self.scroll_anchor is None:     # first frame of the gesture sets the "neutral" height
            self.scroll_anchor = y
            return

        offset = (self.scroll_anchor - y) / self.cam_h   # + = hand moved up
        if abs(offset) < self.scroll_deadzone:
            return

        now = time.time()
        if now - self.last_scroll < 0.05:                # max 20 scroll events / second
            return
        self.last_scroll = now

        # Further from neutral = faster scroll
        strength = min((abs(offset) - self.scroll_deadzone) / 0.2, 1.0)
        amount = max(1, int(strength * MAX_SCROLL))
        pyautogui.scroll(amount if offset > 0 else -amount)