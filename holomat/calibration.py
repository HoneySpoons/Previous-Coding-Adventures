import os
import numpy as np 
import cv2


#-------
#charuco parameters here 
ARUCO_DICT = cv2.aruco.DICT_6X6_250
SQUARES_VERTICALLY = 7
SQUARES_HORIZONTALLY = 5
SQUARE_LENGTH = 0.03
MARKER_LENGTH = 0.015
LENGTH_PX = 640
MARGIN_PX = 20
SAVE_NAME = "charuco.png"

