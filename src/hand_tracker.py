# %% [markdown]
# ## 1. Hand Tracker
# Wraps MediaPipe Hands. Returns all 21 landmarks in pixel coordinates
# so the gesture recognizer can reason about the whole hand, not just two fingertips.

# %%
import cv2
import mediapipe as mp


class HandTracker:
    def __init__(self, detection_conf=0.7, tracking_conf=0.6):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,          # one hand only -> no confusion between hands
            model_complexity=0,       # lighter model = higher FPS = smoother cursor
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )

    def process_frame(self, frame, draw=True):
        """Returns (frame, landmarks). landmarks is a list of 21 (x, y) pixel
        tuples, or None when no hand is visible."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # MediaPipe needs RGB
        rgb.flags.writeable = False
        results = self.hands.process(rgb)

        if not results.multi_hand_landmarks:
            return frame, None

        hand = results.multi_hand_landmarks[0]
        if draw:
            self.mp_draw.draw_landmarks(frame, hand, self.mp_hands.HAND_CONNECTIONS)

        h, w, _ = frame.shape
        landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]
        return frame, landmarks

    def close(self):
        self.hands.close()