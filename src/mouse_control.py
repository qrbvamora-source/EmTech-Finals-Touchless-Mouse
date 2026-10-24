import pyautogui
import numpy as np
import math

# PyAutoGUI safety feature: slam your physical mouse to any corner of the screen to abort the script
pyautogui.FAILSAFE = True

class MouseController:
    def __init__(self, cam_w, cam_h, screen_w, screen_h):
        self.cam_w = cam_w
        self.cam_h = cam_h
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.click_threshold = 40  # Pixel distance threshold to register a pinch/click
        self.clicked = False

    def move_mouse(self, index_coords):
        x, y = index_coords
        
        # Linear interpolation maps camera coordinates to screen coordinates
        screen_x = np.interp(x, (0, self.cam_w), (0, self.screen_w))
        screen_y = np.interp(y, (0, self.cam_h), (0, self.screen_h))
        
        pyautogui.moveTo(screen_x, screen_y)

    def check_click(self, index_coords, thumb_coords):
        ix, iy = index_coords
        tx, ty = thumb_coords
        
        # Calculate Euclidean distance between thumb and index finger
        distance = math.hypot(tx - ix, ty - iy)

        if distance < self.click_threshold:
            if not self.clicked:
                pyautogui.click()
                self.clicked = True
        else:
            self.clicked = False
            
        return distance