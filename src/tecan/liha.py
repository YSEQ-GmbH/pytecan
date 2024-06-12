from .tecan import Tecan
from .entities import Command

__all__ = ['LiHa']


class LiHa:
    def __init__(self, tecan: Tecan, device: str = 'A1'):
        self.__tecan = tecan
        self.__firmware = tecan.firmware
        self.__device = device
        self.__tips_quantity = 0
        self.__actual_machine_x_range = 0
        self.__actual_machine_y_range = 0
        self.__actual_machine_z_range = 0
        self.__active_tips_status: list[bool] = []

    def setup(self):
        if not self.__tecan.is_liha_connected:
            raise Exception('LiHa is not connected')

        response = self.__firmware.send_command(Command(self.__device, 'RNT1'))
        try:
            self.__tips_quantity = int(response.content_str)
            self.__active_tips_status = [True] * self.__tips_quantity
        except ValueError:
            raise Exception('Invalid tips quantity')

        response = self.__firmware.send_command(Command(self.__device, 'RPX5'))
        try:
            self.__actual_machine_x_range = int(response.content_str)
        except ValueError:
            raise Exception('Invalid machine x range')

        response = self.__firmware.send_command(Command(self.__device, 'RPY5'))
        try:
            self.__actual_machine_y_range = int(
                response.content_str.split(',')[0])
        except ValueError:
            raise Exception('Invalid machine y range')

        response = self.__firmware.send_command(Command(self.__device, 'RPZ5'))
        try:
            self.__actual_machine_z_range = int(
                response.content_str.split(',')[0])
        except ValueError:
            raise Exception('Invalid machine z range')

    @property
    def tips_quantity(self):
        return self.__tips_quantity

    def report_current_x_position(self) -> int:
        '''
        Reports the current parameter of the X-axis.

        :return: The current position of the X-axis.
        '''
        response = self.__firmware.send_command(Command(self.__device, 'RPX0'))
        return int(response.content_str)

    def report_current_y_position(self) -> list[int]:
        '''
        Reports the current parameter of the Y and Y-space axis.

        :return: A list containing the current position of the Y and Y-space axis.
        '''
        response = self.__firmware.send_command(Command(self.__device, 'RPY0'))
        return [int(x) for x in response.content_str.split(',')]

    def report_current_z_position(self) -> list[int]:
        '''
        Reports the current parameter of the Z-axis.

        :return: A list of all Z-axis positions for the tips.
        '''
        response = self.__firmware.send_command(Command(self.__device, 'RPZ0'))
        return [int(x) for x in response.content_str.split(',')]

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

    def move_x_to_pos(self, position: int):
        '''
        Moves the X-axis to an absolute position, leaving the other axis position unchanged.

        :param position: The absolute position to move to.
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
            Command(self.__device, f'PAX{position}'))

    def move_y_to_pos(self, position: int, y_space: int = 0):
        '''
        Moves the Y-axis to an absolute position, leaving the other axis position unchanged.

        :param position: The absolute position to move to.
        '''

        if isinstance(position, float):
            position = int(position)

        if not isinstance(position, int):
            self.__firmware.close()
            raise ValueError('Invalid y position: y must be an integer')

        if position < 0 or position > self.__actual_machine_y_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid y position: y must be within the range 0 to ' + str(self.__actual_machine_y_range))

        self.__firmware.send_command(
            Command(self.__device, f'PAY{position}'))

    def move_z_to_pos(self, position: int):
        '''
        Moves the Z-axis to an absolute position, leaving the other axis position unchanged.

        :param position: The absolute position to move to.
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
        self.__firmware.send_command(
            Command(self.__device, f'PAZ{",".join([str(position) if status else "" for status in self.__active_tips_status])}'))

    def set_active_tips_status(self, start_index, end_index, status):
        """
        Set the active status of a range of tips.

        Parameters:
        start_index (int): The starting index of the range.
        end_index (int): The ending index of the range.
        status (bool): The new status for the tips in the range.
        """

        start_index -= 1
        end_index -= 1

        if not 0 <= start_index < len(self.__active_tips_status):
            raise ValueError(
                'Invalid start index: index must be within the range of active tips')

        if not 0 <= end_index < len(self.__active_tips_status):
            raise ValueError(
                'Invalid end index: index must be within the range of active tips')

        for i in range(start_index, end_index + 1):
            self.__active_tips_status[i] = status
