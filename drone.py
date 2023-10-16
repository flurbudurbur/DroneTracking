import djitellopy as tello

class Drone:
    """ Facilitate drone control """

    def __init__(self):
        # self.startup = {'targeted': False}
        self.drone = tello.Tello()
        # self.connection = self.drone.__connect()
        # self.camera = self.drone.__connect_stream()
        # self.control_drone = self.__control_drone(self.startup['targeted'], 0, 0)

    # def __connect(self):
    #     """ Connect to drone """
    #     # disable logging
    #     self.drone.LOGGER.disabled = True
    #     try:
    #         response = self.drone.send_command_with_return('command')
    #         if response.find('ok') != 0:
    #             raise DroneException('Could not connect to drone')
    #         else:
    #             print('Succesfully connected to drone')
    #     except DroneException as de:
    #         exit(de)
        
    # def __connect_stream(self):
    #     """ Connect to drone camera """
    #     try:
    #         response = self.drone.send_command_with_return('streamon')
    #         if response.find('ok') != 0:
    #             raise DroneException('Could not start drone camera')
    #         else:
    #             print('Succesfully started drone camera')

    #     except DroneException as de:
    #         exit(de)
        
    def __control_drone(self, label, cx, cy):
        """ Main drone control function. Calls functions on behalf of the drone """

        if label['targeted']:
            if cx < label['cx']:
                self.__r_left(15)
            elif cx > label['cx']:
                self.__r_right(15)
            # elif cy < label['cy']:
            #     self.up(15)
            # elif cy > label['cy']:
            #     self.down(15)
            else:
                print('No movement necessary')
        else:
            pass

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

    def __get_battery(self):
        """ Get battery percentage """
        try:
            response = self.drone.send_command_with_return('battery?')
            if response.find('ok') != 0:
                raise DroneException('Could not get battery percentage')
            else:
                print(f'{response}')
        except DroneException as de:
            print(de)

class DroneException(Exception):
    def __init_subclass__(self) -> None:
        return super().__init_subclass__()
    
    def overrideException(self, customMsg):
        print(customMsg)
