# %% [markdown]
# ## 4. Main Loop
# Camera -> hand landmarks -> gesture -> mouse action, with an on-screen guide.
# Keys: `q` = quit, `p` = pause/resume (use this when you just want to use your hand normally).

# %%
import time

import cv2
import pyautogui

from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer, Gesture, INDEX_MCP
from mouse_control import MouseController

CAMERA_INDEX = 0
CAM_W, CAM_H = 640, 480
MARGIN = 100  # active-area border in camera pixels

GESTURE_COLORS = {
    Gesture.NONE: (150, 150, 150),
    Gesture.MOVE: (255, 200, 0),
    Gesture.LEFT_CLICK: (0, 255, 0),
    Gesture.RIGHT_CLICK: (0, 140, 255),
    Gesture.SCROLL: (255, 0, 255),
}

GUIDE = [
    "Index finger only    : MOVE",
    "Pinch thumb + index  : LEFT CLICK",
    "Pinch thumb + middle : RIGHT CLICK",
    "Index + middle up    : SCROLL (hand up/down)",
    "Fist / open palm     : IDLE",
    "p = pause   q = quit",
]


def draw_hud(frame, gesture, paused, point, mouse, fps):
    color = GESTURE_COLORS[gesture]

    # Active area: your hand maps to the whole screen only inside this box
    cv2.rectangle(frame, (MARGIN, MARGIN), (CAM_W - MARGIN, CAM_H - MARGIN), (255, 255, 255), 1)

    if point is not None:
        cv2.circle(frame, point, 10, color, cv2.FILLED)

    # Scroll neutral line and dead zone
    if mouse.scroll_anchor is not None:
        dz = int(mouse.scroll_deadzone * CAM_H)
        ay = mouse.scroll_anchor
        cv2.line(frame, (0, ay), (CAM_W, ay), color, 1)
        cv2.rectangle(frame, (0, ay - dz), (CAM_W, ay + dz), color, 1)

    label = "PAUSED" if paused else gesture.value
    cv2.putText(frame, label, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) if paused else color, 2)
    cv2.putText(frame, f"FPS {int(fps)}", (CAM_W - 100, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    for i, line in enumerate(GUIDE):
        y = CAM_H - 10 - (len(GUIDE) - 1 - i) * 20
        cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
    if not cap.isOpened():
        print("Could not open the camera. Try a different CAMERA_INDEX.")
        return

    screen_w, screen_h = pyautogui.size()
    tracker = HandTracker()
    recognizer = GestureRecognizer()
    mouse = MouseController(CAM_W, CAM_H, screen_w, screen_h, margin=MARGIN)

    paused = False
    prev_time = time.time()

    try:
        while True:
            success, frame = cap.read()
            if not success:
                break

            frame = cv2.flip(frame, 1)  # mirror view
            frame, landmarks = tracker.process_frame(frame)

            gesture = recognizer.update(landmarks)

            # The index KNUCKLE (not the fingertip) drives the cursor: it barely moves
            # when you pinch, so clicks don't make the cursor slip off the target.
            point = landmarks[INDEX_MCP] if landmarks else None

            if not paused:
                mouse.update(gesture, point)

            now = time.time()
            fps = 1 / max(now - prev_time, 1e-6)
            prev_time = now

            draw_hud(frame, gesture, paused, point, mouse, fps)
            cv2.imshow("Touchless Mouse", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("p"):
                paused = not paused
    except pyautogui.FailSafeException:
        print("Failsafe triggered (mouse hit a screen corner). Exiting.")
    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()