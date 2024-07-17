from typing import Optional
from .tecan import Tecan
from .entities import Command

__all__ = ['LiHa']


class LiHa:
    def __init__(self, tecan: Tecan, device: str = 'A1', minimum_y_spacing: int = 90):
        self.__tecan = tecan
        self.__firmware = tecan.firmware
        self.__device = device
        self.__tips_quantity = 0
        self.__actual_machine_x_range = 0
        self.__actual_machine_y_range = 0
        self.__actual_machine_z_range = 0
        self.__active_tips_status: list[bool] = []
        self.__minimum_y_spacing = minimum_y_spacing
        self.__y_spacing = 0

    def setup(self):
        if not self.__tecan.is_liha_connected:
            raise Exception('LiHa is not connected')

        response = self.__firmware.send_command(
            Command(self.__device, 'RNT', params=[1]))
        try:
            self.__tips_quantity = int(response.content_str)
            self.__active_tips_status = [True] * self.__tips_quantity
        except ValueError:
            raise Exception('Invalid tips quantity')

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

    @property
    def tips_quantity(self):
        return self.__tips_quantity

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

    def report_current_z_position(self) -> list[int]:
        '''
        Reports the current parameter of the Z-axis.

        :return: A list of all Z-axis positions for the tips.
        '''
        response = self.__firmware.send_command(
            Command(self.__device, 'RPZ', params=[0]))
        return [self.__actual_machine_z_range - int(x) for x in response.content_str.split(',')]

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

        if position < 0 or position > self.__actual_machine_y_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid y position: y must be within the range 0 to ' + str(self.__actual_machine_y_range))

        self.__firmware.send_command(
            Command(self.__device, 'PAY', params=[position, self.__y_spacing]))

    def set_y_spacing(self, spacing: int):
        '''
        Sets the Y-axis spacing.

        Args:
        spacing: The spacing to set.
        '''

        if isinstance(spacing, float):
            spacing = int(spacing)

        if not isinstance(spacing, int):
            self.__firmware.close()
            raise ValueError('Invalid y spacing: y spacing must be an integer')

        self.__y_spacing = self.__minimum_y_spacing + spacing

    @property
    def y_spacing(self) -> int:
        '''
        Returns the Y-axis spacing.
        '''
        return self.__y_spacing

    def move_z_to_pos(self, position: int, speed: Optional[int] = None):
        '''
        Moves the Z-axis to an absolute position, leaving the other axis position unchanged.

        Args:
        position: The absolute position to move to.
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
                Command(self.__device, 'MAZ', params=[position if status else None for status in self.__active_tips_status] + [speed]))
        else:
            self.__firmware.send_command(
                Command(self.__device, 'PAZ', params=[position if status else None for status in self.__active_tips_status]))

    def move_xyz_to_pos(self, x: int = 0, y: int = 0, z: int = 0):
        '''
        Moves the X, Y, and Z-axis to absolute positions.

        Args:
        x: The absolute position of the X-axis.
        y: The absolute position of the Y-axis.
        z: The absolute position of the Z-axis.
        '''

        if isinstance(x, float) or isinstance(y, float) or isinstance(z, float):
            x = int(x)
            y = int(y)
            z = int(z)

        if not isinstance(x, int):
            self.__firmware.close()
            raise ValueError('Invalid x position: x must be an integer')

        if not isinstance(y, int):
            self.__firmware.close()
            raise ValueError('Invalid y position: y must be an integer')

        if not isinstance(z, int):
            self.__firmware.close()
            raise ValueError('Invalid z position: z must be an integer')

        if x < 0 or x > self.__actual_machine_x_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid x position: x must be within the range 0 to ' + str(self.__actual_machine_x_range))

        if y < 0 or y > self.__actual_machine_y_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid y position: y must be within the range 0 to ' + str(self.__actual_machine_y_range))

        if z < 0 or z > self.__actual_machine_z_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid z position: z must be within the range 0 to ' + str(self.__actual_machine_z_range))

        z_position = self.__actual_machine_z_range - z
        z_params = [
            z_position if status else None for status in self.__active_tips_status]

        self.__firmware.send_command(
            Command(self.__device, 'PAA', params=[x, y, self.__y_spacing] + z_params))

    def activate_tip_range(self, start_index: int, end_index: int):
        """
        Activates a range of tips and deactivates all others.
        The activated tips will be used for the next operation.

        Args:
        start_index: The 1-based starting index of the range to activate. For example, to start from the first tip, pass 1.
        end_index: The 1-based ending index of the range to activate. For example, to end at the third tip, pass 3.
        """

        start_index -= 1
        end_index -= 1

        if not 0 <= start_index < len(self.__active_tips_status):
            raise ValueError(
                'Invalid start index: index must be within the range of active tips')

        if not 0 <= end_index < len(self.__active_tips_status):
            raise ValueError(
                'Invalid end index: index must be within the range of active tips')

        if start_index > end_index:
            raise ValueError(
                'Invalid range: start index must be less than or equal to end index')

        self.__active_tips_status = [False] * \
            len(self.__active_tips_status)

        for i in range(start_index, end_index + 1):
            self.__active_tips_status[i] = True

    def activate_single_tip(self, tip_index: int):
        """
        Activates a single tip and deactivates all others.
        The activated tip will be used for the next operation.

        Args:
        tip_index: The 1-based index of the tip to activate. For example, to activate the first tip, pass 1.
        """

        tip_index -= 1

        if not 0 <= tip_index < len(self.__active_tips_status):
            raise ValueError(
                'Invalid tip index: index must be within the range of active tips')

        self.__active_tips_status = [False] * \
            len(self.__active_tips_status)

        self.__active_tips_status[tip_index] = True

    @property
    def active_tips_status(self) -> list[bool]:
        '''
        Returns the status of all tips.
        '''
        return self.__active_tips_status
