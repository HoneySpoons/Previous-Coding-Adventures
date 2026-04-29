import cv2
import mediapipe as mp 
import pyautogui as pag
import numpy as np

mouseDown = False

#set the screen resolution (width,height)
screen_width, screen_height = pag.size()

#Initialize Mediapipe Hand solution
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=.01,
                       min_tracking_confidence=0.1)

mp_drawing = mp.solutions.drawing_utils

#open the camera
cap = cv2.VideoCapture(0)

#error check to make sure the camera is open
if not cap.isOpened():
    print("ERROR")
    exit()

#Main loop
while True:

    #capture frame by fram from camera
    success, frame = cap.read()
    if not success:
        break

    #flip camera frame (if neccessary)

    #Convert frame color from bgr to rgb
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #process the rgb frame with mediapip hands
    results = hands.process(rgb_frame)

    #frame resolution
    frame_height, frame_width, _ = frame.shape

    #DRAW THE HAND ANNOTATIONS ON THE FRAME
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            #Draw Landmarks
            mp_drawing.draw_landmarks(frame, hand_landmarks,mp_hands.HAND_CONNECTIONS)

            #assign fingertips to variables
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            #get the midpoint between thumb and index finger 
            midpoint_x = (index_finger_tip.x + thumb_tip.x) /2
            midpoint_y = (index_finger_tip.y + thumb_tip.y) /2

            #get distance between thumb and index finger 
            distance = np.sqrt((index_finger_tip.x - thumb_tip.x)**2 + (index_finger_tip.y - thumb_tip.y)**2)

            if distance < 0.05 and mouseDown ==False:
                #mouse down
                pag.mouseDown()
                mouseDown = True
            if distance > 0.2 and mouseDown == True:
                #mouse up
                pag.mouseUp()
                mouseDown = False
            
            if mouseDown:
                #draw a circle at midpoint with radius 10
                cv2.circle(frame, (int(midpoint_x*frame_width), int(midpoint_y*frame_height)), 5, (0, 255,0),-1)
            else:
                #draw a circle at midpoint with radius 10
                cv2.circle(frame, (int(midpoint_x*frame_width), int(midpoint_y*frame_height)), 5, (0, 255,0, 1))

            #map the position to the screen resolution
            x_mapped = np.interp(midpoint_x, (0, 1), (screen_width, 0))
            y_mapped = np.interp(midpoint_y, (0,1), (0, screen_height))

            #set the mouse position
            pag.moveTo(x_mapped, y_mapped, duration = 0.05)



    #Dsiplay the resulting frame
    cv2.imshow("Mediapipe Hands", frame)
    cv2.waitKey(1)

#When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



