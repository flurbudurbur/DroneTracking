import cv2 as cv
import numpy as np
import djitellopy as tello
import socket

host = '127.0.0.1'
port = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)
print(f"Server luistert op {host}:{port}")
client_socket, client_address = server_socket.accept()
print(f"Inkomende verbinding van {client_address}")
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
        self.lowest_id_face = {}
        self.lowest_id_face['targeted'] = False
        self.drone = tello.Tello()
        self.cx = None
        self.cy = None
        self.active_tracking = False
        self.commands_sent = 0
        self.commands_threshold = 10

        if settings:
            for setting, value in settings.items():
                sanitized_setting = setting.lower()
                if sanitized_setting in self.settings:
                    # Set the settings to the sanitized keys and values
                    self.settings[sanitized_setting] = value

    def start(self):
        self.drone.connect()
        frame = self.drone.streamon()

        while True:
            frame = self.drone.get_frame_read().frame

            if self.cx is None:
                self.cx = int(frame.shape[1] / 2)
            if self.cy is None:
                self.cy = int(frame.shape[0] / 2)

            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            detections = self.face_cascade.detectMultiScale(
                gray, self.settings['scaleFactor'], self.settings['minNeighbors'])

            self.masks = []

            if self.active_tracking:
                if len(detections) > 0:
                    self.__track_faces(frame, detections)

                else:
                    for label in list(self.tracked_faces.keys()):
                        self.tracked_faces[label]['tracking_lost_count'] += 1
                        if self.tracked_faces[label]['tracking_lost_count'] >= self.settings['maxTrackingLostCount']:
                            del self.tracked_faces[label]

            if self.settings['debug']:
                self.__show_debug_window(frame)
                print(self.tracked_faces)

            # Change camera feed in to bytes and send to LabView

            # Get battery percentage and send to LabView
            battery = self.drone.get_battery()
            battery_bytes = battery.to_bytes(4, 'big')
            client_socket.send(battery_bytes)

            image_bytes = frame.tobytes()
            client_socket.send(image_bytes)
            
            # Checks if LabView buttons are pressed
            data = client_socket.recv(4)
            datastr = str(data, 'UTF-8')
            match datastr:
                case 'rise':
                    if self.drone.is_flying:
                        self.drone.move_up(20)
                    else:
                        self.drone.takeoff()
                case 'face':
                    if self.active_tracking:
                        self.active_tracking = False
                    else:
                        self.active_tracking = True
                case 'land':
                    self.active_tracking = False
                    self.drone.land()
                case 'next':
                    # remove the lowest id face from the tracked faces array
                    del self.tracked_faces[min(self.tracked_faces.keys(), key=lambda x: int(x.split(' ')[1]))]
                case 'stop':
                    self.active_tracking = False
                    self.drone.emergency()
                    exit('Emergency stop button pressed. Exiting program...')
                case _:
                    pass

            if self.lowest_id_face['targeted']:
                if self.cx < self.lowest_id_face['cx']:
                    if self.commands_sent >= self.commands_threshold and self.tracked_faces is not None:
                        self.drone.rotate_counter_clockwise(10)
                        self.commands_sent = 0
                    else:
                        self.commands_sent += 1
                elif self.cx > self.lowest_id_face['cx']:
                    if self.commands_sent >= self.commands_threshold and self.tracked_faces is not None:
                        self.drone.rotate_clockwise(10)
                        self.commands_sent = 0
                    else:
                        self.commands_sent += 1
                elif self.cy < self.lowest_id_face['cy'] and self.tracked_faces is not None:
                    if self.commands_sent >= self.commands_threshold:
                        self.drone.move_up(20)
                        self.commands_sent = 0
                    else:
                        self.commands_sent += 1
                elif self.cy > self.lowest_id_face['cy']:
                    if self.commands_sent >= self.commands_threshold and self.tracked_faces is not None:
                        self.drone.move_down(20)
                        self.commands_sent = 0
                    else:
                        self.commands_sent += 1
                else:
                    print('No movement necessary')

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        self.drone.land()
        cv.destroyAllWindows()

    def __track_faces(self, frame, detections):
        new_faces = {}
        first_enemy_found = False

        for x, y, w, h in detections:
            cx = int(w / 2 + x)
            cy = int(h / 2 + y)
            label, mask = self.__draw_detections(frame, x, y, w, h)
            self.tracking_lost_count = 0
            
            associated = False
            for face_label, face_data in self.tracked_faces.items():
                distance = np.sqrt((cx - face_data['cx'])**2 + (cy - face_data['cy'])**2)
                if distance < self.settings['faceAssociationThreshold']:
                    if label == 'Enemy' and not first_enemy_found:
                        # Associate the detected face with the first enemy found
                        face_data['cx'] = cx
                        face_data['cy'] = cy
                        face_data['distance'] = distance
                        face_data['targeted'] = False
                        # first_enemy_found = True
                    else:
                        face_data['cx'] = cx
                        face_data['cy'] = cy
                        face_data['distance'] = distance
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

    def __draw_detections(self, frame, x, y, w, h):
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