import cv2
import mediapipe as mp
import numpy as np
from picamera2 import Picamera2

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# ---------- Tunable thresholds ----------
KNEE_THRESH_UP = 150.0     # "standing" / top position
KNEE_THRESH_DOWN = 95.0   # squat depth threshold (increase if you're not going deep)
# ---------------------------------------

def calculate_angle(a, b, c):
    """Return the angle at point b (in degrees) for points a-b-c."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle

# Picamera2 setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "BGR888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

squat_counter = 0
stage = "start"  # start -> down -> up -> start

with mp_pose.Pose(
    model_complexity=0,                 # fastest (good for Pi)
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    while True:
        frame = picam2.capture_array()  # BGR

        # MediaPipe needs RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = pose.process(rgb)
        rgb.flags.writeable = True

        lknee_angle = None
        rknee_angle = None

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            # Helper to get (x,y) in normalized coords
            def xy(landmark_enum):
                p = lm[landmark_enum.value]
                return [p.x, p.y]

            # Left leg points
            lhip = xy(mp_pose.PoseLandmark.LEFT_HIP)
            lknee = xy(mp_pose.PoseLandmark.LEFT_KNEE)
            lankle = xy(mp_pose.PoseLandmark.LEFT_ANKLE)

            # Right leg points
            rhip = xy(mp_pose.PoseLandmark.RIGHT_HIP)
            rknee = xy(mp_pose.PoseLandmark.RIGHT_KNEE)
            rankle = xy(mp_pose.PoseLandmark.RIGHT_ANKLE)

            # Angles
            lknee_angle = calculate_angle(lhip, lknee, lankle)
            rknee_angle = calculate_angle(rhip, rknee, rankle)

            # Draw skeleton
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # ---------- Squat state machine ----------
            # Only run logic if both angles exist
            if lknee_angle is not None and rknee_angle is not None:
                # Start -> Down (knees bend)
                if stage == "start" and lknee_angle < KNEE_THRESH_UP and rknee_angle < KNEE_THRESH_UP:
                    stage = "down"

                # Down -> Up (hit depth)
                elif stage == "down" and lknee_angle < KNEE_THRESH_DOWN and rknee_angle < KNEE_THRESH_DOWN:
                    stage = "up"

                # Up -> Start (stand back up => count rep)
                elif stage == "up" and lknee_angle > KNEE_THRESH_UP and rknee_angle > KNEE_THRESH_UP:
                    stage = "start"
                    squat_counter += 1
                    print("Total squats:", squat_counter)
            # ----------------------------------------

        # Overlay UI
        cv2.putText(frame, f"Squats: {squat_counter}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"Stage: {stage}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        if lknee_angle is not None:
            cv2.putText(frame, f"L knee: {lknee_angle:.0f}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        if rknee_angle is not None:
            cv2.putText(frame, f"R knee: {rknee_angle:.0f}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Squat Counter (ESC to quit)", frame)

        # ESC to quit
        if cv2.waitKey(1) & 0xFF == 27:
            break

cv2.destroyAllWindows()
picam2.stop()
