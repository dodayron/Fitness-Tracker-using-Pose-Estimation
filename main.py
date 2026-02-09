from picamera2 import Picamera2
import cv2
import mediapipe as mp
from exercise_loader import load_exercise

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

current_exercise = load_exercise("squat")

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "BGR888", "size": (640, 480)}
))
picam2.start()

with mp_pose.Pose(model_complexity=0) as pose:
    while True:
        frame = picam2.capture_array()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            angle = current_exercise.update(results.pose_landmarks.landmark)
            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.putText(frame, f"{current_exercise.name}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            cv2.putText(frame, f"Reps: {current_exercise.reps}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            cv2.putText(frame, f"State: {current_exercise.stage}",
                        (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
                        
            # Angle (only if computed)
            if angle is not None:
                cv2.putText(frame, f"Angle: {angle:.1f} deg",
                        (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('1'):
            current_exercise = load_exercise("squat")
        elif key == ord('2'):
            current_exercise = load_exercise("curl_right")
        elif key == 27:
            break

        cv2.imshow("Exercise Tracker", frame)

cv2.destroyAllWindows()
picam2.stop()
