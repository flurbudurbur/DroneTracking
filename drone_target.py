from FaceDetect.facedetect import FaceDetect
import math
import numpy as np
import cv2

class DroneTracker(FaceDetect):
    def follow(self):
        # get frame dimensions
        frame = (self.frame.shape[1]//2, self.frame.shape[0]//2)
        try:
            for (top, right, bottom, left), label in self.detections:

                # draw circle on forehead
                center_x = int((left + right) / 2)
                center_y = int((top + bottom) / 2)
                forehead = int((top + (bottom - top)) * 0.25)

                _, color_frame = self.frame.read()
                hsv_frame = self.canvas.cvtColor(color_frame, self.canvas.COLOR_BGR2HSV)

                # # Pick pixel value
                # pixel_center = hsv_frame[center_y, center_x]
                # hue_value = pixel_center[0]

                # pixel_center_bgr = color_frame[center_y, center_x]
                # b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])

                # print(hue_value)

                # draw circle on forehead
                self.canvas.circle(self.frame, (center_x, forehead), 15, (0, 0, 0), 3)

                # calculate the difference between the center and the face coordinates
                diff = (frame[0] - center_x, frame[1] - center_y)

                # deal with NaN
                if math.isnan(diff[0]):
                    diff[0] = 0
                if math.isnan(diff[1]):
                    diff[1] = 0

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
        except Exception:
            return

        


        

facedetector = DroneTracker({'custom': 'follow', 'method': 'recognize', 'known-faces': {'Sebas': 'resources/sebas.jpg'}})
# facedetector = DroneTracker({'custom': 'colorfind'})

try:
    facedetector.start()
except Exception as e:
    print(e)