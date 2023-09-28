import cv2 as cv
import djitellopy as tello
from djitellopy import TelloException

class FaceDetector:
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
        # connect to drone
        self.__connect()
        self.__connect_stream()

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
                
                label = self.__draw_detections(frame, x, y, w, h, cx)

                diff = (int(self.settings['size'][0] / 2 - cx),
                        int(self.settings['size'][1] / 2 - cy))

                # move the drone for enemies
                self.__control_drone(diff, label)

            cv.imshow('Cam girls :3', frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()
    
    #===# Drone utility functions #===#
    def __connect(self):
        # disable logging
        self.drone.LOGGER.disabled = True
        try:
            response = self.drone.send_command_with_return('command')
            if response.find('ok') != 0:
                raise DroneException('Could not connect to drone')
            else:
                print('Succesfully connected to drone')
        except DroneException as de:
            print(de)
        
    def __connect_stream(self):
        try:
            response = self.drone.send_command_with_return('streamon')
            if response.find('ok') != 0:
                raise TelloException('Could not start drone camera')
            else:
                print('Succesfully started drone camera')
        except TelloException:
            raise TelloException('Could not start stream')
        
    def __control_drone(self, diff, label):
        if diff[0] > self.settings['deadZone'] and label == "Enemy":
            self.__r_left(15)
        elif diff[0] < -self.settings['deadZone'] and label == "Enemy":
            self.__r_right(15)
        elif diff[1] > self.settings['deadZone']:
            self.__move_down(20)
        elif diff[1] < -self.settings['deadZone']:
            self.__move_up(20)
        else:
            print('No movement necessary')

    def __draw_detections(self, frame, x, y, w, h, cx):
        forehead = int(y / 1.1)
        hsv_frame = cv.cvtColor(frame, cv.COLOR_RGB2HSV)

        # Pick pixel value
        pixel_center = hsv_frame[forehead, cx]
        hue_value = pixel_center[0]
        
        # if hue value is around green, mark target as friendly
        if hue_value > 80 and hue_value < 120:
            label = 'Friendly'
        # if hue value is around red, mark target as enemy
        elif hue_value > 340 and hue_value < 360 or hue_value > 0 and hue_value < 10:
            label = 'Enemy'
        else:
            label = 'Unknown'

        b = 255 if label == 'Unknown' else 0
        g = 255 if label != 'Enemy' else 0
        r = 255 if label == 'Enemy' else 0

        bgr_colors = (b, g, r)

        cv.rectangle(frame, (x, y), (x+w, y+h), bgr_colors, 1)
        cv.putText(frame, label, (x + 6, y - 6),
                    cv.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 1)
        return label


    #===# Drone movement functions #===#
    def __r_left(self, val):
        try:
            response = self.drone.send_command_with_return('left {}'.format(val))
            if response.find('ok') != 0:
                raise DroneException('Could not rotate left')
            else:
                print('Succesfully rotated left')
        except DroneException as de:
            print(de)
        
    def __r_right(self, val):
        try:
            response = self.drone.send_command_with_return('right {}'.format(val))
            if response.find('ok') != 0:
                raise DroneException('Could not rotate right')
            else:
                print('Succesfully rotated right')
        except DroneException as de:
            print(de)
    
    def __move_up(self, val):
        try:
            response = self.drone.send_command_with_return('up {}'.format(val))
            if response.find('ok') != 0:
                raise DroneException('Could not move up')
            else:
                print('Succesfully moved up')
        except DroneException as de:
            print(de)

    def __move_down(self, val):
        try:
            response = self.drone.send_command_with_return('down {}'.format(val))
            if response.find('ok') != 0:
                raise DroneException('Could not move down')
            else:
                print('Succesfully moved down')
        except DroneException as de:
            print(de)

class DroneException(Exception):
    def __init_subclass__(self) -> None:
        return super().__init_subclass__()
    
    def overrideException(self, customMsg):
        print(customMsg)

if __name__ == '__main__':
    detector = FaceDetector()
    detector.start()
