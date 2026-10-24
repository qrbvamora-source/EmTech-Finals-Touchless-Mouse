import cv2
import pyautogui
from hand_tracker import HandTracker
from mouse_control import MouseController

def main():
    # Initialize camera (0 is usually the default laptop webcam)
    cap = cv2.VideoCapture(0)
    cam_w, cam_h = 640, 480
    cap.set(3, cam_w)
    cap.set(4, cam_h)

    # Get local desktop resolution automatically
    screen_w, screen_h = pyautogui.size()
    
    # Instantiate custom modules
    tracker = HandTracker()
    mouse = MouseController(cam_w, cam_h, screen_w, screen_h)

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Flip frame horizontally for a natural mirror effect
        frame = cv2.flip(frame, 1)

        # Process frame to find hand landmarks
        frame, landmarks = tracker.process_frame(frame)

        # If both index and thumb are detected on screen, execute mouse logic
        if 'index' in landmarks and 'thumb' in landmarks:
            mouse.move_mouse(landmarks['index'])
            mouse.check_click(landmarks['index'], landmarks['thumb'])

        # Display the visual feedback window
        cv2.imshow("Touchless Mouse Feed", frame)

        # Press 'q' on your keyboard to quit the program cleanly
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()