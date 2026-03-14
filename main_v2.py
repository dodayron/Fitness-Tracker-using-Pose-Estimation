from picamera2 import Picamera2
import cv2
import mediapipe as mp
import numpy as np
import time

from datetime import datetime
from database import insert_session

import sound_manager

# Importing from the v2 loader and LED manager
from exercise_loader_v2 import load_exercise
from led_manager import LEDManager

# Initialize MediaPipe
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

# Load Initial Exercise
current_exercise = load_exercise("squat")

# track previous reps
previous_reps = 0;

# Initialise session_start so the first save works
session_start = datetime.now()

# Setup Camera (RPi)
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "BGR888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

#set LEDs 
leds = LEDManager()
leds.clear()

# FPS Calculation variables
p_time = 0

def draw_progress_bar(image, angle, ex_class):
    # Interpolate angle to bar height (normalized 0 to 1)
    # Mapping: Rest Angle (0%) -> Peak Angle (100%)
    per = np.interp(angle, (ex_class.peak_thresh, ex_class.rest_thresh), (100, 0))
    bar = np.interp(angle, (ex_class.peak_thresh, ex_class.rest_thresh), (100, 400))
    
    # Check if rep target reached for color change
    color = (0, 255, 255) # Yellow default
    if per == 100:
        color = (0, 255, 0) # Green if hit depth
    
    # Draw Bar background
    cv2.rectangle(image, (580, 100), (620, 400), (0, 255, 0), 1)
    # Draw Bar Fill
    cv2.rectangle(image, (580, int(bar)), (620, 400), color, cv2.FILLED)
    # Draw Percentage text
    cv2.putText(image, f'{int(per)}%', (565, 75), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0) as pose:
    print("Starting Exercise Tracker V2... Press 'Esc' to quit.")
    
    while True:
        try:
            # Capture frame
            frame = picam2.capture_array()
            
            # FPS Calculation
            c_time = time.time()
            fps = 1 / (c_time - p_time)
            p_time = c_time

            # MediaPipe Processing
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False 
            results = pose.process(rgb)
            rgb.flags.writeable = True

            # Draw Landmarks
            if results.pose_landmarks:
                mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # Logic Update
                angle = current_exercise.update(results.pose_landmarks.landmark)

                # UI Overlay
                # 1. Info Box Background
                cv2.rectangle(frame, (0,0), (250, 150), (245, 117, 16), -1)
                
                # 2. Text Data
                cv2.putText(frame, f"{current_exercise.name}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                cv2.putText(frame, str(current_exercise.reps), (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3)
                cv2.putText(frame, f"Stage: {current_exercise.stage}", (10, 130), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
                
                cv2.putText(frame, f"FPS: {int(fps)}", (500, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0, 255), 2)

                # 3. Progress Bar & Angle + sounds
                if angle is not None:
                    #on screen progress bar
                    draw_progress_bar(frame, angle, current_exercise)
                    
                    #physical LED update
                    per = np.interp(angle, (current_exercise.peak_thresh, current_exercise.rest_thresh), (100,0))
                    
                    leds.update_bar(per)
                    leds.update_reps(current_exercise.reps)
                if current_exercise.reps > previous_reps:
                    # Check if it's the 8th nultiple rep
                    if current_exercise.reps % 8 == 0 and current_exercise.reps > 0:
                        sound_manager.chimes.play() 
                    else:
                        sound_manager.rep_beep.play()
                    
                    # Update tracker
                    previous_reps = current_exercise.reps
                    
                    
            ######## Key Controls #######
            key = cv2.waitKey(1) & 0xFF
            if key == ord('1'):
                # END current session
                session_end = datetime.now()
                previous_reps = 0;

                insert_session(
                    exercise = current_exercise.name,
                    reps = current_exercise.reps,
                    sets = 1, # only one for now
                    date = session_start.strftime("%Y-%m-%d"), 
                    #strftime converts datetime to string to match the SQLite storage format
                    start_time = session_start.strftime("%H:%M:%S"),
                    end_time = session_end.strftime("%H:%M:%S")
                )
                
                sound_manager.squat_instruct.play()                
                current_exercise = load_exercise("squat")
                current_exercise.reps = 0 
            elif key == ord('2'):
                # END current session
                session_end = datetime.now()
                previous_reps = 0;

                insert_session(
                    exercise = current_exercise.name,
                    reps = current_exercise.reps,
                    sets = 1,
                    date = session_start.strftime("%Y-%m-%d"),
                    start_time = session_start.strftime("%H:%M:%S"),
                    end_time = session_end.strftime("%H:%M:%S")
                )

                # START new session
                sound_manager.rCurl_instruct.play()
                current_exercise = load_exercise("curl_right")
                session_start = datetime.now()

            elif key == ord('3'):
                # END current session
                session_end = datetime.now()
                previous_reps = 0;

                insert_session(
                    exercise = current_exercise.name,
                    reps = current_exercise.reps,
                    sets = 1,
                    date = session_start.strftime("%Y-%m-%d"),
                    start_time = session_start.strftime("%H:%M:%S"),
                    end_time = session_end.strftime("%H:%M:%S")
                )
                
                current_exercise = load_exercise("curl_left")
                current_exercise.reps = 0
            elif key == 27: # ESC
                session_end = datetime.now()
                leds.clear()

                insert_session(
                    exercise=current_exercise.name,
                    reps=current_exercise.reps,
                    sets=1,
                    date=session_start.strftime("%Y-%m-%d"),
                    start_time=session_start.strftime("%H:%M:%S"),
                    end_time=session_end.strftime("%H:%M:%S")
                )
                break
            
            # Show Feed
            cv2.imshow("RPi Fitness Tracker V2", frame)

        except Exception as e:
            print(f"Error: {e}")
            leds.clear() #turn off leds if crash
            pygame.quit() #turn off audio manager
            break

cv2.destroyAllWindows()
picam2.stop()
