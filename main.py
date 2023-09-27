import cv2 as cv
import djitellopy as tello

class FaceDetector():
    """ Face detector class """
    def __init__(self, settings=None):
        self.settings = self.DEFAULT_SETTINGS
        self.drone = tello.Tello()
        # self.stream = self.drone
        self.faces = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        if settings:
            for setting in settings:

                # Sanitize the key
                sanitized_setting = setting.lower()

                # Get the value and sanitize if string, otherwise take as is
                val = settings.get(setting)
                val = val.lower().strip() if type(val) is str else val

                # Set the settings to the sanitized keys and values
                self.settings[sanitized_setting] = val if type(val) is bool or val else self.settings[sanitized_setting]

    DEFAULT_SETTINGS = {
        'scaleFactor': 1.1,
        'minNeighbors': 4,
        'size': (480, 360)
    }
    
    def start(self):
        self.drone.connect()
        self.drone.streamon()
        # self.drone.takeoff()

        while True:
            frame = cv.cvtColor(self.drone.get_frame_read().frame, cv.COLOR_BGR2RGB)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            detections = self.faces.detectMultiScale(gray, self.settings['scaleFactor'], self.settings['minNeighbors'])
            for x, y, w, h in detections:
                center_x = int((x + w) / 2)
                center_y = int((y + h) / 2)
                forehead = int(y / 1.1)
                hsv_frame = cv.cvtColor(frame, cv.COLOR_RGB2HSV)

                # # Pick pixel value
                pixel_center = hsv_frame[forehead, center_x]
                hue_value = pixel_center[0]

                # if hue value is around green, mark target as friendly
                if hue_value > 80 and hue_value < 120:
                    label = 'Friendly'
                # elif hue_value > 350 and hue_value < 359 or hue_value > 0 and hue_value < 10:
                elif hue_value > 340 and hue_value < 360 or hue_value > 0 and hue_value < 10:
                    label = 'Enemy'
                else:
                    label = 'Unknown'

                b = 255 if label == 'Unknown' else 0
                g = 255 if label != 'Enemy' else 0
                r = 255 if label == 'Enemy' else 0
                cv.rectangle(frame, (x, y), (x+w, y+h), (b, g, r), 1)
                cv.putText(frame, label, (x + 6, y - 6), cv.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 1)

                diff = (int(self.settings['size'][0] / 2 - center_x), int(self.settings['size'][1] / 2 - center_y))

                # # move the drone for enemies
                # if diff[0] > 50 and label == 'Enemy':
                #     if self.input == 'drone':
                #         self.drone.rotate_counter_clockwise(20)
                #     else:
                #         print('drone moves left')
                # elif diff[0] < -50 and label == 'Enemy':
                #     if self.input == 'drone':
                #         self.drone.rotate_clockwise(20)
                #     else:
                #         print('drone moves right')
                # if diff[1] > 50 and label == 'Enemy':
                #     if self.input == 'drone':
                #         self.drone.move_down(20)
                #     else:
                #         print('drone moves down')
                # elif diff[1] < -50 and label == 'Enemy':
                #     if self.input == 'drone':
                #         self.drone.move_up(20)
                #     else:
                #         print('drone moves up')
                # if diff[0] < 50 and diff[0] > -50 and label == 'Enemy':
                #     print('stop left/right')
                # if diff[1] < 50 and diff[1] > -50 and label == 'Enemy':
                #     print('stop up/down')
            cv.waitKey(1)

            cv.imshow('Cam girls :3', frame)
            
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
        # self.drone.land()
        cv.destroyAllWindows()
    
if __name__ == '__main__':
    detector = FaceDetector()
    detector.start()