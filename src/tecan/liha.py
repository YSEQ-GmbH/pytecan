from typing import Optional
from .tecan import Tecan
from .entities import Command
from .firmware.standard import calculate_tip_select


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

        if position < -800 or position > self.__actual_machine_y_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid y position: y must be within the range -800 to ' + str(self.__actual_machine_y_range))

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
                Command(self.__device, 'MAZ', params=[position if status else None for status in self.__active_tips_status] + [speed]))
        else:
            self.__firmware.send_command(
                Command(self.__device, 'PAZ', params=[position if status else None for status in self.__active_tips_status]))

    def move_z_to_detect_liquid_and_submerge(self, z_start: int, z_max: int, submerge_depth: int = 10):
        '''
        Moves the Z-axis until the liquid is detected.
        Then, the Z-axis is submerged to a specified depth.

        Args:
            z_start: The starting position of the Z-axis to detect the liquid.
            z_max: The maximum position of the Z-axis to detect the liquid.
            submerge_depth: The depth to submerge the Z-axis after detecting the liquid.
        '''
        z_start = self.actual_machine_z_range - z_start
        z_max = self.actual_machine_z_range - z_max

        if not 0 <= z_start <= self.actual_machine_z_range:
            raise ValueError(
                'Invalid z_start: z_start must be within the range 0 to ' + str(self.actual_machine_z_range))

        if not 0 <= z_max <= self.actual_machine_z_range:
            raise ValueError(
                'Invalid z_max: z_max must be within the range 0 to ' + str(self.actual_machine_z_range))

        if not 0 <= submerge_depth <= z_max:
            raise ValueError(
                'Invalid submerge_depth: submerge_depth must be within the range 0 to ' + z_max)

        active_tips = [i+1 for i,
                       tip in enumerate(self.active_tips_status) if tip]

        self.__firmware.send_command(
            command=Command(self.__device, 'MET', params=[calculate_tip_select(active_tips), submerge_depth, z_start,  z_max]))

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

        if y < -800 or y > self.__actual_machine_y_range:
            self.__firmware.close()
            raise ValueError(
                'Invalid y position: y must be within the range -800 to ' + str(self.__actual_machine_y_range))

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

    def activate_tip_custom(self, tips: list[int]):
        """
        Activates a custom list of tips and deactivates all others.
        The activated tips will be used for the next operation.

        Args:
            tips: A list of 1-based tip indexes to activate. For example, to activate the first and third tips, pass [1, 3].
        """

        for tip in tips:
            if not 0 < tip <= len(self.__active_tips_status):
                raise ValueError(
                    'Invalid tip index: index must be within the range of active tips')

        self.__active_tips_status = [False] * \
            len(self.__active_tips_status)

        for tip in tips:
            self.__active_tips_status[tip - 1] = True

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

    def activate_all_tips(self):
        """
        Activates all tips.
        All tips will be used for the next operation.
        """

        self.__active_tips_status = [True] * len(self.__active_tips_status)

    @property
    def active_tips_status(self) -> list[bool]:
        '''
        Returns the status of all tips.
        '''
        return self.__active_tips_status

    def aspirate(self, volume: int = 20, speed: int = 9):
        '''
        Aspirates a liquid or air from the current position of the Z-axis.

        Args:
            volume: The volume to aspirate.
            speed: The speed of aspiration.
                   SpeedCode:
                   0  = 6000 HS/s;  21 = 160 HS/s
                   1  = 5600 HS/s;  22 = 150 HS/s
                   2  = 5000 HS/s;  23 = 140 HS/s
                   3  = 4400 HS/s;  24 = 130 HS/s
                   4  = 3800 HS/s;  25 = 120 HS/s
                   5  = 3200 HS/s;  26 = 110 HS/s
                   6  = 2600 HS/s;  27 = 100 HS/s
                   7  = 2200 HS/s;  28 = 90 HS/s
                   8  = 2000 HS/s;  29 = 80 HS/s
                   9  = 1800 HS/s;  30 = 70 HS/s
                   10 = 1600 HS/s;  31 = 60 HS/s
                   11 = 1400 HS/s;  32 = 50 HS/s
                   12 = 1200 HS/s;  33 = 40 HS/s
                   13 = 1000 HS/s;  34 = 30 HS/s
                   14 = 800 HS/s;   35 = 20 HS/s
                   15 = 600 HS/s;   36 = 18 HS/s
                   16 = 400 HS/s;   37 = 16 HS/s
                   17 = 200 HS/s;   38 = 14 HS/s
                   18 = 190 HS/s;   39 = 12 HS/s
                   19 = 180 HS/s;   40 = 10 HS/s
                   20 = 170 HS/s (default = 9)
        '''
        volume = int(volume * 3.15)

        if volume < 1 or volume > 3150:
            raise ValueError(
                'Invalid volume: volume must be within the range 1 to 1000')

        if speed < 0 or speed > 40:
            raise ValueError(
                'Invalid speed: speed must be within the range 0 to 40')

        self.__firmware.send_commands(
            [Command(f'D{index + 1}', f'S{speed}OP{volume}R') for index,
             status in enumerate(self.__active_tips_status) if status],
            group_channel='D'
        )

    def dispense(self, volume: int = 20, speed: int = 9):
        '''
        Dispenses a liquid or air from the current position of the Z-axis.

        Args:
            volume: The volume to dispense.
            speed: The speed of dispensing.
                   SpeedCode:
                   0  = 6000 HS/s;  21 = 160 HS/s
                   1  = 5600 HS/s;  22 = 150 HS/s
                   2  = 5000 HS/s;  23 = 140 HS/s
                   3  = 4400 HS/s;  24 = 130 HS/s
                   4  = 3800 HS/s;  25 = 120 HS/s
                   5  = 3200 HS/s;  26 = 110 HS/s
                   6  = 2600 HS/s;  27 = 100 HS/s
                   7  = 2200 HS/s;  28 = 90 HS/s
                   8  = 2000 HS/s;  29 = 80 HS/s
                   9  = 1800 HS/s;  30 = 70 HS/s
                   10 = 1600 HS/s;  31 = 60 HS/s
                   11 = 1400 HS/s;  32 = 50 HS/s
                   12 = 1200 HS/s;  33 = 40 HS/s
                   13 = 1000 HS/s;  34 = 30 HS/s
                   14 = 800 HS/s;   35 = 20 HS/s
                   15 = 600 HS/s;   36 = 18 HS/s
                   16 = 400 HS/s;   37 = 16 HS/s
                   17 = 200 HS/s;   38 = 14 HS/s
                   18 = 190 HS/s;   39 = 12 HS/s
                   19 = 180 HS/s;   40 = 10 HS/s
                   20 = 170 HS/s (default = 9)
        '''
        volume = int(volume * 3.15)

        if volume < 1 or volume > 3150:
            raise ValueError(
                'Invalid volume: volume must be within the range 1 to 1000')

        if speed < 0 or speed > 40:
            raise ValueError(
                'Invalid speed: speed must be within the range 0 to 40')

        self.__firmware.send_commands(
            [Command(f'D{index + 1}', f'S{speed}OD{volume}R') for index,
             status in enumerate(self.__active_tips_status) if status],
            group_channel='D'
        )

    def wash_tips(self, x_position: int = 0, y_position: int = 1059, z_position: int = 700):
        '''
        Washes the tips at a specified XYZ position.

        Args:
            x_position: The absolute position of the X-axis.
            y_position: The absolute position of the Y-axis.
            z_position: The absolute position of the Z-axis.
        '''
        self.move_xyz_to_pos(x=x_position, y=y_position, z=z_position)

        self.__firmware.send_commands(
            [Command(f'D{index + 1}', 'YIP100OS9OD100R') for index,
             status in enumerate(self.__active_tips_status) if status],
            group_channel='D'
        )

        self.__firmware.send_commands(
            [Command(f'D{index + 1}', 'OV3600A0R') for index,
             status in enumerate(self.__active_tips_status) if status],
            group_channel='D'
        )

        self.__firmware.send_commands(
            [Command(f'D{index + 1}', 'BR') for index,
             status in enumerate(self.__active_tips_status) if status],
            group_channel='D'
        )

        self.__firmware.send_command(
            Command('O1', 'AFI', params=[1, 38, 8]))

        self.__firmware.send_commands(
            [Command(f'D{index + 1}', 'M500IR') for index,
             status in enumerate(self.__active_tips_status) if status],
            group_channel='D'
        )

        self.__firmware.send_commands(
            [Command(f'D{index + 1}', 'IV3600P1500OA0R') for index,
             status in enumerate(self.__active_tips_status) if status],
            group_channel='D'
        )
