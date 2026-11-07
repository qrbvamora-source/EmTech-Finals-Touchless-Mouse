# %% [markdown]
# ## 2. Gesture Recognizer
# Turns 21 hand landmarks into ONE of five gestures. Three things make it reliable:
# 1. Pinch distance is divided by hand size, so it works at any distance from the camera.
# 2. Hysteresis: a pinch starts at a tight threshold and only ends at a looser one (no flicker).
# 3. A gesture must be held for several frames before it becomes "confirmed".

# %%
import math
from enum import Enum


class Gesture(Enum):
    NONE = "NONE"
    MOVE = "MOVE"
    LEFT_CLICK = "LEFT CLICK"
    RIGHT_CLICK = "RIGHT CLICK"
    SCROLL = "SCROLL"


# MediaPipe landmark indices
WRIST = 0
THUMB_TIP = 4
INDEX_MCP, INDEX_PIP, INDEX_TIP = 5, 6, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP = 9, 10, 12
RING_PIP, RING_TIP = 14, 16
PINKY_PIP, PINKY_TIP = 18, 20


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class GestureRecognizer:
    def __init__(self, pinch_on=0.28, pinch_off=0.42, stable_frames=3):
        self.pinch_on = pinch_on        # pinch STARTS below this (x hand size)
        self.pinch_off = pinch_off      # pinch ENDS above this (x hand size)
        self.stable_frames = stable_frames
        self._pinch_index = False
        self._pinch_middle = False
        self._candidate = Gesture.NONE
        self._count = 0
        self.current = Gesture.NONE     # the confirmed gesture

    # ---- helpers --------------------------------------------------------
    @staticmethod
    def _extended(lm, tip, pip):
        """Finger counts as extended if its tip is clearly farther from the wrist
        than its middle joint. Works even if the hand is tilted."""
        return _dist(lm[tip], lm[WRIST]) > _dist(lm[pip], lm[WRIST]) * 1.25

    def _raw_gesture(self, lm):
        size = max(_dist(lm[WRIST], lm[MIDDLE_MCP]), 1.0)  # hand-size reference
        d_idx = _dist(lm[THUMB_TIP], lm[INDEX_TIP]) / size
        d_mid = _dist(lm[THUMB_TIP], lm[MIDDLE_TIP]) / size

        # Pinch with hysteresis; only the closer finger can pinch
        thr_i = self.pinch_off if self._pinch_index else self.pinch_on
        thr_m = self.pinch_off if self._pinch_middle else self.pinch_on
        self._pinch_index = d_idx < thr_i and d_idx <= d_mid
        self._pinch_middle = d_mid < thr_m and d_mid < d_idx

        idx = self._extended(lm, INDEX_TIP, INDEX_PIP)
        mid = self._extended(lm, MIDDLE_TIP, MIDDLE_PIP)
        ring = self._extended(lm, RING_TIP, RING_PIP)
        pinky = self._extended(lm, PINKY_TIP, PINKY_PIP)

        if self._pinch_index:
            return Gesture.LEFT_CLICK
        if self._pinch_middle:
            return Gesture.RIGHT_CLICK
        if idx and mid and not ring and not pinky:
            return Gesture.SCROLL
        if idx and not mid and not ring and not pinky:
            return Gesture.MOVE
        return Gesture.NONE   # fist, open palm, anything unclear -> do nothing

    # ---- public ---------------------------------------------------------
    def update(self, landmarks):
        """Call once per frame. Returns the confirmed (debounced) gesture."""
        raw = Gesture.NONE if landmarks is None else self._raw_gesture(landmarks)

        if raw == self.current:
            self._candidate, self._count = raw, 0
        elif raw == self._candidate:
            self._count += 1
            if self._count >= self.stable_frames:
                self.current, self._count = raw, 0
        else:
            self._candidate, self._count = raw, 1
        return self.current