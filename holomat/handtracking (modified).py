import cv2
import mediapipe as mp
import pyautogui as pag
import numpy as np
from filterpy.kalman import KalmanFilter

mouseDown = False

# Set the screen resolution (width, height)
screen_width, screen_height = pag.size()

# Initialize Mediapipe Hand solution
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.01,
                       min_tracking_confidence=0.1)

mp_drawing = mp.solutions.drawing_utils

# Open the camera
cap = cv2.VideoCapture(0)

# Error check to make sure the camera is open
if not cap.isOpened():
    print("ERROR")
    exit()

# Initialize Kalman filter for smoothing hand position
kf = KalmanFilter(dim_x=4, dim_z=2)  # 4D state (x, y, dx, dy), 2D measurement (x, y)
kf.F = np.array([[1, 0, 1, 0],
                 [0, 1, 0, 1],
                 [0, 0, 1, 0],
                 [0, 0, 0, 1]])
kf.H = np.array([[1, 0, 0, 0],
                 [0, 1, 0, 0]])
kf.Q = np.eye(4) * 1  # Process noise covariance
kf.R = np.eye(2) * 0.1   # Measurement noise covariance
kf.x = np.array([0, 0, 0, 0])  # Initial state estimate
kf.P = np.eye(4) * 10         # Initial covariance matrix

# Main loop
while True:
    # Capture frame by frame from camera
    success, frame = cap.read()
    if not success:
        break

    # Flip camera frame (if necessary)

    # Convert frame color from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the RGB frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    # Frame resolution
    frame_height, frame_width, _ = frame.shape

    # Draw the hand annotations on the frame
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw Landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Assign fingertips to variables
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Get the midpoint between thumb and index finger
            midpoint_x = (index_finger_tip.x + thumb_tip.x) / 2
            midpoint_y = (index_finger_tip.y + thumb_tip.y) / 2

            # Get distance between thumb and index finger
            distance = np.sqrt((index_finger_tip.x - thumb_tip.x) ** 2 + (index_finger_tip.y - thumb_tip.y) ** 2)

            # Apply Kalman filter to smooth hand position
            kf.predict()
            kf.update(np.array([[midpoint_x], [midpoint_y]]))
            smoothed_midpoint_x, smoothed_midpoint_y = kf.x[0], kf.x[1]

            if distance < 0.05 and not mouseDown:
                # Mouse down
                pag.mouseDown()
                mouseDown = True
            if distance > 0.2 and mouseDown:
                # Mouse up
                pag.mouseUp()
                mouseDown = False

            if mouseDown:
                # Draw a circle at midpoint with radius 5
                cv2.circle(frame, (int(smoothed_midpoint_x * frame_width), int(smoothed_midpoint_y * frame_height)), 5, (0, 255, 0), -1)
            else:
                # Draw a circle at midpoint with radius 5
                cv2.circle(frame, (int(smoothed_midpoint_x * frame_width), int(smoothed_midpoint_y * frame_height)), 5, (0, 255, 0, 1))

            # Map the position to the screen resolution
            x_mapped = np.interp(smoothed_midpoint_x, (0, 1), (screen_width, 0))
            y_mapped = np.interp(smoothed_midpoint_y, (0, 1), (0, screen_height))

            # Set the mouse position
            pag.moveTo(x_mapped, y_mapped, duration=0.1)

    # Display the resulting frame
    cv2.imshow("Mediapipe Hands", frame)
    cv2.waitKey(1)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



