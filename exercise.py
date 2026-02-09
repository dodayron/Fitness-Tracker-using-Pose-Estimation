import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

class Exercise:
    def __init__(self, config):
        self.name = config["name"]
        self.angle_points = config["angle_points"]
        self.sides = config["sides"]
        self.thresholds = config["thresholds"]
        self.stage = config["start_stage"]
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
        return 360 - angle if angle > 180 else angle

    def get_angle(self, landmarks):
        angles = []
        for side in self.sides:
            p1 = self._get_point(landmarks, side, self.angle_points[0])
            p2 = self._get_point(landmarks, side, self.angle_points[1])
            p3 = self._get_point(landmarks, side, self.angle_points[2])
            angles.append(self._calculate_angle(p1, p2, p3))
        return min(angles)

    def update(self, landmarks):
        angle = self.get_angle(landmarks)

        if self.stage in ["start", "down"] and angle < self.thresholds["up"]:
            self.stage = "down"
        elif self.stage == "down" and angle < self.thresholds["down"]:
            self.stage = "up"
        elif self.stage == "up" and angle > self.thresholds["up"]:
            self.stage = "start"
            self.reps += 1

        return angle
