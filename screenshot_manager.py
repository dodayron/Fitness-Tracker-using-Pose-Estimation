import cv2
import time
from datetime import datetime

class ScreenshotManager:
    def __init__(self, interval=10):
        self.interval = interval
        self.last_time = time.time()

    def update(self, frame):
        if time.time() - self.last_time >= self.interval:
            filename = f"screenshot_{datetime.now().strftime('%H%M%S')}.png"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
            self.last_time = time.time()