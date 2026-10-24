import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        # min_detection_confidence prevents the tracker from flickering
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        # MediaPipe requires RGB format, but OpenCV captures in BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        landmarks_dict = {}

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the connections on the hand
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Extract coordinates for Index Finger Tip (8) and Thumb Tip (4)
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    
                    if id == 8:
                        landmarks_dict['index'] = (cx, cy)
                    elif id == 4:
                        landmarks_dict['thumb'] = (cx, cy)
                        
        return frame, landmarks_dict