import cv2 as cv
import numpy as np
from djitellopy import *
from drone import Drone

class FaceDetector:
    """ Face detector class """

    def __init__(self, settings=None, debug=False):
        self.settings = {
            'scaleFactor': 1.2,
            'minNeighbors': 4,
            'size': (1280, 720),
            'maxTrackingLostCount': 10,
            'faceAssociationThreshold': 50,
            'foreheadRatio': 1.1,
            'morphKernelSize': (5, 5),
            'debug': debug,
        }
        self.face_cascade = cv.CascadeClassifier(
            'haarcascade_frontalface_default.xml')
        self.tracked_faces = {}
        self.tracking_lost_count = 0
        self.face_counter = 0
        self.mask_window_name = 'Masks'
        self.lowest_id_face = None
        self.drone = Drone()
        self.cx = None
        self.cy = None

        if settings:
            for setting, value in settings.items():
                sanitized_setting = setting.lower()
                if sanitized_setting in self.settings:
                    # Set the settings to the sanitized keys and values
                    self.settings[sanitized_setting] = value

    def start(self):
        # capture = cv.VideoCapture(0)
        capture = self.drone.connect()
        frame = self.drone.connect_stream()

        while True:
            frame = self.drone.background_frame_read().frame
            # if not ret:
            #     break

            if self.cx is None:
                self.cx = int(frame.shape[1] / 2)
            if self.cy is None:
                self.cy = int(frame.shape[0] / 2)

            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            detections = self.face_cascade.detectMultiScale(
                gray, self.settings['scaleFactor'], self.settings['minNeighbors'])

            self.masks = []

            if len(detections) > 0:
                self.__track_faces(frame, detections)

            else:
                for label in list(self.tracked_faces.keys()):
                    self.tracked_faces[label]['tracking_lost_count'] += 1
                    if self.tracked_faces[label]['tracking_lost_count'] >= self.settings['maxTrackingLostCount']:
                        del self.tracked_faces[label]

            # print(self.tracked_faces)

            if self.settings['debug']:
                self.__show_debug_window(frame)

            cv.imshow('Webcam Feed', frame)
            self.drone.control_drone(self.lowest_id_face, self.cx, self.cy)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        # capture.release()
        self.drone.land()
        cv.destroyAllWindows()

    def __track_faces(self, frame, detections):
        new_faces = {}
        first_enemy_found = False

        for x, y, w, h in detections:
            cx = int((x + w) / 2)
            cy = int((y + h) / 2)
            label, mask = self.__draw_detections(frame, x, y, w, h, cx)
            self.tracking_lost_count = 0

            
            associated = False
            for face_label, face_data in self.tracked_faces.items():
                distance = np.sqrt((cx - face_data['cx'])**2 + (cy - face_data['cy'])**2)
                if distance < self.settings['faceAssociationThreshold']:
                    if label == 'Enemy' and not first_enemy_found:
                        # Associate the detected face with the first enemy found
                        face_data['cx'] = cx
                        face_data['cy'] = cy
                        face_data['targeted'] = False
                        # first_enemy_found = True
                    else:
                        face_data['cx'] = cx
                        face_data['cy'] = cy
                        face_data['targeted'] = False
                    associated = True
                    new_faces[face_label] = face_data
                    break

            if not associated:
                self.face_counter += 1
                new_faces[f'{label} {self.face_counter}'] = {
                    'cx': cx,
                    'cy': cy,
                    'id': f'{self.face_counter}',
                    'tracking_lost_count': 0,
                    'targeted': False
                }

            if self.settings['debug']:
                self.masks.append(mask)

        self.tracked_faces = new_faces

        # Print the label of the face with the lowest ID
        self.lowest_id_face = min(self.tracked_faces.values(), key=lambda x: int(x['id']))
        self.lowest_id_face['targeted'] = True

        # print(self.tracked_faces)

    def __draw_detections(self, frame, x, y, w, h, cx):
        forehead = int(y / self.settings['foreheadRatio'])
        hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        friendly_lower = np.array([40, 50, 50])
        friendly_upper = np.array([80, 255, 255])
        enemy_lower = np.array([0, 50, 50])
        enemy_upper = np.array([20, 255, 255])

        friendly_mask = cv.inRange(hsv_frame, friendly_lower, friendly_upper)
        enemy_mask = cv.inRange(hsv_frame, enemy_lower, enemy_upper)

        friendly_mask = cv.morphologyEx(friendly_mask, cv.MORPH_CLOSE, np.ones(self.settings['morphKernelSize'], np.uint8))
        enemy_mask = cv.morphologyEx(enemy_mask, cv.MORPH_CLOSE, np.ones(self.settings['morphKernelSize'], np.uint8))

        friendly_pixel_count = np.sum(friendly_mask[forehead, :])
        enemy_pixel_count = np.sum(enemy_mask[forehead, :])

        if friendly_pixel_count > enemy_pixel_count:
            label = 'Friendly'
        elif enemy_pixel_count > friendly_pixel_count:
            label = 'Enemy'
        else:
            label = 'Unknown'

        b = 255 if label == 'Unknown' else 0
        g = 255 if label != 'Enemy' else 0
        r = 255 if label == 'Enemy' else 0

        for _, face_data in self.tracked_faces.items():
            if face_data['targeted'] and face_data['tracking_lost_count'] < self.settings['maxTrackingLostCount']:
                label = f'{label} - Targeted'
            face_data['targeted'] = False
        
        bgr_colors = (b, g, r)

        cv.rectangle(frame, (x, y), (x+w, y+h), bgr_colors, 1)
        cv.putText(frame, label, (x + 6, y - 6),
                    cv.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 1)

        colored_mask = cv.merge((friendly_mask, np.zeros_like(friendly_mask), enemy_mask))

        return label, colored_mask

    def __show_debug_window(self, frame):
        merged_mask = np.zeros_like(frame)
        for mask in self.masks:
            merged_mask = cv.bitwise_or(merged_mask, mask)

        cv.imshow(self.mask_window_name, merged_mask)

if __name__ == '__main__':
    custom_settings = {
        'scaleFactor': 1.2,             # Adjust the scale factor for face detection (smaller values for more detections)
        'minNeighbors': 4,              # Adjust the minimum neighbors for face detection (higher values for fewer false positives)
        'maxTrackingLostCount': 10,     # Maximum number of frames to keep tracking a lost face
        'faceAssociationThreshold': 50, # Threshold for associating detected faces with tracked faces (adjust based on distance)
        'foreheadRatio': 1.1,           # Adjust the forehead region ratio for color analysis
        'morphKernelSize': (5, 5),      # Adjust the kernel size for morphological operations to reduce mask noise
        'debug': False,                  # Enable or disable the debug mode
    }

    detector = FaceDetector(settings=custom_settings)
    detector.start()