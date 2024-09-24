from typing import Optional
from .tecan import Tecan
from .entities import Command


__all__ = ['Roma']


class Roma:
    def __init__(self, tecan: Tecan, device: str = 'R1'):
        self.__tecan = tecan
        self.__firmware = tecan.firmware
        self.__device = device
        self.__actual_machine_x_range = 0
        self.__actual_machine_y_range = 0
        self.__actual_machine_z_range = 0
        self.__actual_machine_r_range = 0
        self.__actual_machine_g_range = 0

    def setup(self):
        if not self.__tecan.is_roma_connected:
            raise Exception('Roma is not connected')

        response = self.__firmware.send_command(
            Command(self.__device, 'RPX', params=[5]))
        try:
            self.__actual_machine_x_range = int(response.content_str)
        except ValueError:
            raise Exception('Invalid machine x range')

        response = self.__firmware.send_command(
            Command(self.__device, 'RPY', params=[5]))
        try:
            self.__actual_machine_y_range = int(
                response.content_str.split(',')[0])
        except ValueError:
            raise Exception('Invalid machine y range')

        response = self.__firmware.send_command(
            Command(self.__device, 'RPZ', params=[5]))
        try:
            self.__actual_machine_z_range = int(
                response.content_str.split(',')[0])
        except ValueError:
            raise Exception('Invalid machine z range')

        response = self.__firmware.send_command(
            Command(self.__device, 'RPR', params=[5]))
        try:
            self.__actual_machine_r_range = int(response.content_str)
        except ValueError:
            raise Exception('Invalid machine r range')

        response = self.__firmware.send_command(
            Command(self.__device, 'RPG', params=[5]))
        try:
            self.__actual_machine_g_range = int(response.content_str)
        except ValueError:
            raise Exception('Invalid machine g range')

    def report_current_x_position(self) -> int:
        '''
        Reports the current parameter of the X-axis.

        :return: The current position of the X-axis.
        '''
        response = self.__firmware.send_command(
            Command(self.__device, 'RPX', params=[0]))
        return int(response.content_str)

    def report_current_y_position(self) -> list[int]:
        '''
        Reports the current parameter of the Y and Y-space axis.

        :return: A list containing the current position of the Y and Y-space axis.
        '''
        response = self.__firmware.send_command(
            Command(self.__device, 'RPY', params=[0]))
        return [int(x) for x in response.content_str.split(',')]

    def report_current_z_position(self) -> int:
        '''
        Reports the current parameter of the Z-axis.

        :return: A list of all Z-axis positions for the tips.
        '''
        response = self.__firmware.send_command(
            Command(self.__device, 'RPZ', params=[0]))
        return self.__actual_machine_z_range - int(response.content_str)

    def report_current_r_position(self) -> int:
        '''
        Reports the current parameter of the Rotator-axis.

        :return: The current position of the Rotator-axis.
        '''
        response = self.__firmware.send_command(
            Command(self.__device, 'RPR', params=[0]))
        return int(response.content_str)

    def report_current_g_position(self) -> int:
        '''
        Reports the current parameter of the Gripper-axis.

        :return: The current position of the Gripper-axis.
        '''
        response = self.__firmware.send_command(
            Command(self.__device, 'RPG', params=[0]))
        return int(response.content_str)

    @property
    def actual_machine_x_range(self) -> int:
        '''
        Returns the actual machine X range.
        '''
        return self.__actual_machine_x_range

    @property
    def actual_machine_y_range(self) -> int:
        '''
        Returns the actual machine Y range.
        '''
        return self.__actual_machine_y_range

    @property
    def actual_machine_z_range(self) -> int:
        '''
        Returns the actual machine Z range.
        '''
        return self.__actual_machine_z_range

    @property
    def actual_machine_r_range(self) -> int:
        '''
        Returns the actual machine R range.
        '''
        return self.__actual_machine_r_range

    @property
    def actual_machine_g_range(self) -> int:
        '''
        Returns the actual machine G range.
        '''
        return self.__actual_machine_g_range

    def move_x_to_pos(self, position: int):
        '''
        Moves the X-axis to an absolute position, leaving the other axis position unchanged.

        Args:
            position: The absolute position to move to.
        '''

        if isinstance(position, float):
            position = int(position)

        if not isinstance(position, int):
            self.__firmware.close()
            raise ValueError('Invalid x position: x must be an integer')

        if position < 0 or position > self.__actual_machine_x_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid x position: x must be within the range 0 to ' + str(self.__actual_machine_x_range))

        self.__firmware.send_command(
            Command(self.__device, 'PAX', params=[position]))

    def move_y_to_pos(self, position: int):
        '''
        Moves the Y-axis to an absolute position, leaving the other axis position unchanged.

        Args:
            position: The absolute position to move to.
        '''

        if isinstance(position, float):
            position = int(position)

        if not isinstance(position, int):
            self.__firmware.close()
            raise ValueError('Invalid y position: y must be an integer')

        if position < -800 or position > self.__actual_machine_y_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid y position: y must be within the range -800 to ' + str(self.__actual_machine_y_range))

        self.__firmware.send_command(
            Command(self.__device, 'PAY', params=[position]))

    def move_z_to_pos(self, position: int, speed: Optional[int] = None):
        '''
        Moves the Z-axis to an absolute position, leaving the other axis position unchanged.

        Args:
            position: The absolute position to move to.
            speed: The speed of movement. speed in 0.1 mm/s [1..4000]
        '''

        if isinstance(position, float):
            position = int(position)

        if not isinstance(position, int):
            self.__firmware.close()
            raise ValueError('Invalid z position: z must be an integer')

        if position < 0 or position > self.__actual_machine_z_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid z position: z must be within the range 0 to ' + str(self.__actual_machine_z_range))

        position = self.__actual_machine_z_range - position

        if speed is not None:
            if not 0 <= speed <= 4000:
                raise ValueError(
                    'Invalid speed: speed must be within the range 0 to 4000')
            self.__firmware.send_command(
                Command(self.__device, 'MAZ', params=[position, speed]))
        else:
            self.__firmware.send_command(
                Command(self.__device, 'PAZ', params=[position]))

    def rotate_to_degree(self, degree: int):
        """
        Moves the Rotator-axis to a specified absolute position, leaving the other axis positions unchanged.

        Args:
            degree (int): The absolute position to move to, in degrees. Valid range is [0..270].

        Raises:
            ValueError: If the degree is outside the valid range.
        """
        if not (0 <= degree <= 270):
            raise ValueError("Degree must be within the range [0..270]")
        # Add the implementation to move the rotator to the specified angle

        degree = degree * 10

        if isinstance(degree, float):
            degree = int(degree)

        if not isinstance(degree, int):
            self.__firmware.close()
            raise ValueError('Invalid r position: r must be an integer')

        if degree < 0 or degree > self.__actual_machine_r_range:
            self.__firmware.close()
            raise ValueError(
                f'Invalid r position: r must be within the range 0 to 270')

        self.__firmware.send_command(
            Command(self.__device, 'PAR', params=[degree]))

    def move_g_to_pos(self, position: int):
        '''
        Moves the Gripper-axis to an absolute position, leaving the other axis position unchanged.

        Args:
            position: The absolute position to move to.
        '''

        if isinstance(position, float):
            position = int(position)

        if not isinstance(position, int):
            self.__firmware.close()
            raise ValueError('Invalid g position: g must be an integer')

        if position < 0 or position > self.__actual_machine_g_range:
            self.__firmware.close()
            raise ValueError(
                f'Invalid g position: g must be within the range 0 to {self.__actual_machine_g_range}')

        self.__firmware.send_command(
            Command(self.__device, 'PAG', params=[position]))
