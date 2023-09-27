import cv2 as cv
import djitellopy as tello

class FaceDetector():
    """ Face detector class """

    def __init__(self, settings=None):
        self.settings = {
            'scaleFactor': 1.2,
            'minNeighbors': 4,
            'size': (480, 360),
            'deadZone': 10
        }
        self.drone = tello.Tello()
        self.faces = cv.CascadeClassifier(
            'haarcascade_frontalface_default.xml')
        self.first_face = []

    def start(self):
        self.drone.connect()
        self.drone.streamon()

        self.drone.takeoff()
        while True:
            frame = cv.cvtColor(
                self.drone.get_frame_read().frame, cv.COLOR_BGR2RGB)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            detections = self.faces.detectMultiScale(
                gray, self.settings['scaleFactor'], self.settings['minNeighbors'])

            # print(self.first_face)
            for x, y, w, h in detections:
                cx = int((x + w) / 2)
                cy = int((y + h) / 2)
                forehead = int(y / 1.1)
                hsv_frame = cv.cvtColor(frame, cv.COLOR_RGB2HSV)

                # # Pick pixel value
                pixel_center = hsv_frame[forehead, cx]
                hue_value = pixel_center[0]

                # if hue value is around green, mark target as friendly
                if hue_value > 80 and hue_value < 120:
                    label = 'Friendly'
                # elif hue_value > 340 and hue_value < 360 or hue_value > 0 and hue_value < 10:
                elif hue_value > 340 and hue_value < 360 or hue_value > 0 and hue_value < 10:
                    label = 'Enemy'
                else:
                    label = 'Unknown'

                b = 255 if label == 'Unknown' else 0
                g = 255 if label != 'Enemy' else 0
                r = 255 if label == 'Enemy' else 0
                cv.rectangle(frame, (x, y), (x+w, y+h), (b, g, r), 1)
                cv.putText(frame, label, (x + 6, y - 6),
                           cv.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 1)

                diff = (int(self.settings['size'][0] / 2 - cx),
                        int(self.settings['size'][1] / 2 - cy))

                # move the drone for enemies
                if diff[0] > self.settings['deadZone'] and label == "Enemy":
                    self.drone.rotate_counter_clockwise(15)
                    print('drone moves left')
                elif diff[0] < -self.settings['deadZone'] and label == "Enemy":
                    self.drone.rotate_clockwise(15)
                if diff[1] > self.settings['deadZone']:
                    print('drone moves down')
                    # self.drone.move_down(20)
                elif diff[1] < -self.settings['deadZone']:
                    print('drone moves up')
                    # self.drone.move_up(20)
                if diff[0] < self.settings['deadZone'] and diff[0] > -self.settings['deadZone']:
                    print('stop left/right')
                if diff[1] < self.settings['deadZone'] and diff[1] > -self.settings['deadZone']:
                    print('stop up/down')

            cv.imshow('Cam girls :3', frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()


if __name__ == '__main__':
    detector = FaceDetector()
    detector.start()
