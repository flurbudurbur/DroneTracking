from FaceDetect.facedetect import FaceDetect
import math
import numpy as np
import cv2

class DroneTracker(FaceDetect):
    def follow(self):
        # get coordinates of the face
        try:
            coords = self.detections[0][0]
        except Exception:
            coords = [0, 0, 0, 0]
            return 
        # get frame dimensions
        frame = (self.frame.shape[1]//2, self.frame.shape[0]//2)
        # calculate the difference between the center and the face coordinates
        diff = (frame[0] - coords[2], frame[1] - coords[3])

        # deal with NaN
        if math.isnan(diff[0]):
            diff[0] = 0
        if math.isnan(diff[1]):
            diff[1] = 0

        print(diff)
        # move the drone
        if diff[0] > 50:
            print('drone moves left')
        elif diff[0] < -50:
            print('drone moves right')
        if diff[1] > 50:
            print('drone moves down')
        elif diff[1] < -50:
            print('drone moves up')
        if diff[0] < 50 and diff[0] > -50:
            print('stop left/right')
        if diff[1] < 50 and diff[1] > -50:
            print('stop up/down')

        # get the face 

        bgr_boundaries = [([51, 205, 50], [63, 255, 62])]
        for lower, upper in bgr_boundaries:
            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")

            # mask = cv2.inRange(, lower, upper)

facedetector = DroneTracker({'custom': 'follow'})

try:
    facedetector.start()
except Exception as e:
    print(e)