import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

class Exercise:
    def __init__(self, config):
        self.name = config["name"]
        self.angle_points = config["angle_points"]
        self.sides = config["sides"]
        # rest_thresh = Angle when limb is extended (e.g., Standing for squat)
        # peak_thresh = Angle at full contraction (e.g., Deep squat)
        self.rest_thresh = config["thresholds"]["rest"]
        self.peak_thresh = config["thresholds"]["peak"]
        
        self.stage = "rest" # States: 'rest', 'peak'
        self.reps = 0

    def _get_point(self, landmarks, side, joint):
        landmark_name = f"{side.upper()}_{joint}"
        return landmarks[getattr(mp_pose.PoseLandmark, landmark_name).value]

    def _calculate_angle(self, a, b, c):
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])

        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - \
                  np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def get_angle(self, landmarks):
        angles = []
        for side in self.sides:
            try:
                p1 = self._get_point(landmarks, side, self.angle_points[0])
                p2 = self._get_point(landmarks, side, self.angle_points[1])
                p3 = self._get_point(landmarks, side, self.angle_points[2])
                angles.append(self._calculate_angle(p1, p2, p3))
            except (AttributeError, IndexError):
                pass # Landmark not visible
        
        if not angles:
            return None
        return min(angles)

    def update(self, landmarks):
        angle = self.get_angle(landmarks)

        if angle is None:
            return None

        # State Machine: Rest -> Peak -> Rest
        
        # 1. Check if we reached the Peak
        if angle < self.peak_thresh:
            self.stage = "peak"
            
        # 2. Check if we returned to Rest AND were previously at peak
        if angle > self.rest_thresh and self.stage == "peak":
            self.stage = "rest"
            self.reps += 1

        return angle
