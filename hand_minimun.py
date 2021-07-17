import math
import cv2
import mediapipe as mp
import keyboard
import win32api, win32con
import time

capture = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.75)

mpDraw = mp.solutions.drawing_utils


def trackJoint(index, color=(0,  0,0), showData=False):
    cv2.circle(image,
               (math.floor(handLandmarks.landmark[index].x * 650), math.floor(handLandmarks.landmark[index].y * 475)),
               radius=1,
               color=color,
               thickness=5
               )  # draw a point at the point of the pointer finger
    if showData:
        print(handLandmarks.landmark[index].x , handLandmarks.landmark[index].y)

    return {
        "x": handLandmarks.landmark[index].x,
        "y": handLandmarks.landmark[index].y
    }


wasPinching = False
linesCoords = []

print("running image capture...")
while True:
    success, image = capture.read()
    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # mediapipe only reads rgb images

    hands_results = hands.process(imgRGB)
    # print(hands_results.multi_hand_landmarks)


    if hands_results.multi_hand_landmarks:  # check if there are hands
        for handLandmarks in hands_results.multi_hand_landmarks:
            f_pointer_end = trackJoint(8)
            f_pointer_end_int = math.floor( f_pointer_end * 10)

            f_thumb_end = trackJoint(4)
            f_thumb_end = math.floor(f_thumb_end * 10)

            distanceBetweenFingers_x = f_pointer_end['x'] - f_thumb_end['x']
            if distanceBetweenFingers_x < 0:
                distanceBetweenFingers_x = distanceBetweenFingers_x * -1


            distanceBetweenFingers_y = f_pointer_end['y'] - f_thumb_end['y']
            if distanceBetweenFingers_y < 0:
                distanceBetweenFingers_y = distanceBetweenFingers_y * -1


            closedFingersDistance = 0.085

            isPinching = distanceBetweenFingers_x < closedFingersDistance and distanceBetweenFingers_y < closedFingersDistance

            if isPinching:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, f_thumb_end["x"], f_thumb_end["y"], 0,0)

                if not wasPinching:
                    print("Started to Pinch")
                    startingPos = (
                         math.floor((f_pointer_end["x"] + f_thumb_end["x"]) * 10 / 2 * 65),
                         math.floor((f_pointer_end["y"] + f_thumb_end["y"]) * 10 / 2 * 47.5)
                    )
                    wasPinching = True

            else:
                if wasPinching:
                    print("Stopped to Pinch")
                    endingPos = (
                        math.floor((f_pointer_end["x"] + f_thumb_end["x"]) * 10 / 2 * 65),
                        math.floor((f_pointer_end["y"] + f_thumb_end["y"]) * 10 / 2 * 47.5)
                    )
                    wasPinching = False

                    linesCoords.append([startingPos, endingPos])
                    print(f'linha feita de {startingPos} à {endingPos}')
        win32api.SetCursorPos(((math.floor(win32api.GetSystemMetrics(0) * f_thumb_end['x']) * -1) + win32api.GetSystemMetrics(0), math.floor(win32api.GetSystemMetrics(1) * f_thumb_end['y'])))


    # for coords in linesCoords:
    #    cv2.line(image, coords[0], coords[1], color=(20, 20, 120), thickness=5 )

    # if keyboard.is_pressed("q"):
    #    linesCoords = []


    cv2.imshow("Hand Recognition with python", image)
    cv2.waitKey(1)  # not wait for any key to show the next frame

