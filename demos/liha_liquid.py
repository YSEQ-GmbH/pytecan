from tecan import Tecan, Firmware, LiHa
from tecan.entities import Command


def calculate_tip_select(tips):
    """
    Calculate the TipSelect value for the given list of tips.

    Args:
    tips (list of int): List of tip numbers to be selected (e.g., [2, 4, 6, 8]).

    Returns:
    int: The calculated TipSelect value.
    """
    tip_select = 0
    for tip in tips:
        # Set the corresponding bit for each tip number
        tip_select |= 1 << (tip - 1)
    return tip_select


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    tips = [1, 2]

    liha.activate_tip_range(tips[0], tips[1])
    # liha.activate_single_tip(tips[0])

    # x, y, z : 2550, 1375, 1140
    # x, y, z : 1470, 1400, 500

    while True:
        liha.move_xyz_to_pos(x=1470, y=1400, z=500)

        z_start = liha.actual_machine_z_range - 500
        z_max = liha.actual_machine_z_range - 1500

        tecan.firmware.send_command(
            command=Command('A1', 'MDT', params=[calculate_tip_select(tips), 10, z_start,  z_max]))

        print(liha.report_current_z_position())

        liha.move_xyz_to_pos()

        x = input('Press any key to continue...')
        if x == 'q':
            break

    tecan.close()


if __name__ == '__main__':
    main()
