import djitellopy as tello

class Drone(tello.Tello):
    """ Facilitate drone control """

    def __init__(self):
        self.drone = tello.Tello()
        self.connect = self.__connect()
        self.connect_stream = self.__connect_stream()
        self.control_drone = self.__control_drone(None, None, None)
        self.left = self.__r_left()
        self.right = self.__r_right()
        self.up = self.__move_up()
        self.down = self.__move_down()

    def __connect(self):
        """ Connect to drone """
        # disable logging
        self.drone.LOGGER.disabled = True
        try:
            response = self.drone.send_command_with_return('command')
            if response.find('ok') != 0:
                raise DroneException('Could not connect to drone')
            else:
                print('Succesfully connected to drone')
        except DroneException as de:
            exit(de)
        
    def __connect_stream(self):
        """ Connect to drone camera """
        try:
            response = self.drone.send_command_with_return('streamon')
            if response.find('ok') != 0:
                raise DroneException('Could not start drone camera')
            else:
                print('Succesfully started drone camera')

        except DroneException as de:
            exit(de)
        
    def __control_drone(self, label, cx, cy):
        """ Main drone control function. Calls functions on behalf of the drone """
        if label['targeted']:
            if cx < label['cx']:
                self.left(15)
            elif cx > label['cx']:
                self.right(15)
            elif cy < label['cy']:
                self.up(15)
            elif cy > label['cy']:
                self.down(15)
            else:
                print('No movement necessary')

    #===# Drone movement functions #===#
    def __r_left(self, val):
        """ Rotate left """
        try:
            response = self.drone.send_command_with_return('ccw {}'.format(val))
            if response.find('ok') != 0:
                raise DroneException('Could not rotate left')
            else:
                print('Succesfully rotated left')
        except DroneException as de:
            print(de)
        
    def __r_right(self, val):
        """ Rotate right """
        try:
            response = self.drone.send_command_with_return('cw {}'.format(val))
            if response.find('ok') != 0:
                raise DroneException('Could not rotate right')
            else:
                print('Succesfully rotated right')
        except DroneException as de:
            print(de)
    
    def __move_up(self, val):
        """ Move up """
        try:
            response = self.drone.send_command_with_return('up {}'.format(val))
            if response.find('ok') != 0:
                raise DroneException('Could not move up')
            else:
                print('Succesfully moved up')
        except DroneException as de:
            print(de)

    def __move_down(self, val):
        """ Move down """
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
