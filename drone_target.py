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
        
        # bgr_boundaries = [([51, 205, 50], [63, 255, 62])]
        # for lower, upper in bgr_boundaries:
        #     lower = np.array(lower, dtype = "uint8")
        #     upper = np.array(upper, dtype = "uint8")

            # mask = cv2.inRange(, lower, upper)

        while True:
            faceframe = coords[0]
            self.stream = self.canvas.cvtColor(self.frame, self.canvas.COLOR_BGR2HSV)
            height, width, _ = frame.shape
            cx = int(coords[2] / 2)
            cy = int(coords[3] / 2)

            # Pick pixel value
            pixel_center = hsv_frame[cy, cx]
            hue_value = pixel_center[0]

            color = "Undefined"
            if hue_value < 5:
                color = "RED"
            elif hue_value < 22:
                color = "ORANGE"
            elif hue_value < 33:
                color = "YELLOW"
            elif hue_value < 78:
                color = "GREEN"
            elif hue_value < 131:
                color = "BLUE"
            elif hue_value < 170:
                color = "VIOLET"
            else:
                color = "RED"

            pixel_center_bgr = frame[cy, cx]
            b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])

            self.canvas.rectangle(frame, (cx - 220, 10), (cx + 200, 120), (255, 255, 255), -1)
            self.canvas.putText(frame, color, (cx - 200, 100), 0, 3, (b, g, r), 5)
            self.canvas.circle(frame, (cx, cy), 5, (25, 25, 25), 3)

            self.canvas.imshow("Frame", frame)
            key = self.canvas.waitKey(1)
            if key == 27:
                break

facedetector = DroneTracker({'custom': 'follow'})
# facedetector = DroneTracker({'custom': 'colorfind'})

try:
    facedetector.start()
except Exception as e:
    print(e)