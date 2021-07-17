import math
import cv2
import mediapipe as mp
import keyboard
import win32api, win32con
import time

"""
TODO LIST
- scroll
- make borders easier to access (get a sensibility configuration)
"""

capture = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.75)

mpDraw = mp.solutions.drawing_utils


def trackJoint(index, color=(0, 0, 0), showData=False):
    cv2.circle(image,
               (math.floor(handLandmarks.landmark[index].x * 650), math.floor(handLandmarks.landmark[index].y * 475)),
               radius=1,
               color=color,
               thickness=5
               )  # draw a point at the point of the pointer finger
    if showData:
        print(handLandmarks.landmark[index].x , handLandmarks.landmark[index].y)

    return {
        "index": index,
        "x": handLandmarks.landmark[index].x,
        "y": handLandmarks.landmark[index].y
    }

def isTouching(j1, j2, closedFingersDistance = 0.055):
    distanceBetweenFingers_x = j1['x'] - j2['x']
    if distanceBetweenFingers_x < 0:
        distanceBetweenFingers_x = distanceBetweenFingers_x * -1

    distanceBetweenFingers_y = j1['y'] - j2['y']
    if distanceBetweenFingers_y < 0:
        distanceBetweenFingers_y = distanceBetweenFingers_y * -1

    result = distanceBetweenFingers_x < closedFingersDistance and distanceBetweenFingers_y < closedFingersDistance

    if result:
        trackJoint(j1["index"], (0,255,0))
        trackJoint(j2["index"], (0,255,0))

    return result




wasPinching = False
wasPinkyDown = False
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
            f_thumb_end = trackJoint(4)
            f_pinky_end = trackJoint(20)
            f_pinky_start = trackJoint(17)
            f_palm = trackJoint(0)

            isPinching = isTouching(f_pointer_end, f_thumb_end)

            if isPinching:

                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, math.floor(f_thumb_end["x"] * 10),
                                     math.floor(f_thumb_end["y"]), 0, 0)
                time.sleep(.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, math.floor(f_thumb_end["x"] * 10),
                                     math.floor(f_thumb_end["y"]), 0, 0)

                if not wasPinching:
                    pinch_startingPos = (
                         math.floor((f_pointer_end["x"] + f_thumb_end["x"]) * 10 / 2 * 65),
                         math.floor((f_pointer_end["y"] + f_thumb_end["y"]) * 10 / 2 * 47.5)
                    )
                    wasPinching = True
            else:
                if wasPinching:

                    pinch_endingPos = (
                        math.floor((f_pointer_end["x"] + f_thumb_end["x"]) * 10 / 2 * 65),
                        math.floor((f_pointer_end["y"] + f_thumb_end["y"]) * 10 / 2 * 47.5)
                    )
                    wasPinching = False

                    linesCoords.append([pinch_startingPos, pinch_endingPos])

            isPinkyDown = isTouching(f_pinky_end, f_pinky_start)

            if isPinkyDown and not wasPinkyDown:
                pinkyDown_startingPos = f_palm

           # if not isPinkyDown and wasPinkyDown:
            if False:
                pinkyDown_endingPos = f_palm

                if pinkyDown_startingPos["y"] > pinkyDown_endingPos["y"]:
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, f_thumb_end["x"], f_thumb_end["x"], 1, 0)
                elif pinkyDown_startingPos["y"] < pinkyDown_endingPos["y"]:
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, f_thumb_end["x"], f_thumb_end["x"], 1, 0)

    for coords in linesCoords:
        cv2.line(image, coords[0], coords[1], color=(20, 20, 120), thickness=5)


  #      win32api.SetCursorPos(((math.floor(win32api.GetSystemMetrics(0) * f_thumb_end['x'] * -1) + win32api.GetSystemMetrics(0)),
     #                          (math.floor(win32api.GetSystemMetrics(1) * f_thumb_end['y']))))



    if keyboard.is_pressed("q"):
       linesCoords = []


    cv2.imshow("Hand Recognition with python", image)
    cv2.waitKey(1)  # not wait for any key to show the next frame

