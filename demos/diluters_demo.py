from tecan import Tecan, Firmware, LiHa
from tecan.entities import Command


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    liha.activate_single_tip(1)
    liha.move_y_to_pos(liha.actual_machine_y_range/2 - 350)
    liha.move_z_to_pos(700)

    device = f'D1'

    tecan.firmware.send_command(
        Command(device, 'YIP1000OS9OD1000R'))

    liha.move_z_to_pos(0)

    liha.move_x_to_pos(2550)
    liha.move_y_to_pos((liha.actual_machine_y_range/2 - 350)+330)
    liha.move_z_to_pos(750)

    # tecan.firmware.send_command(
    #     Command(device, 'OS5IP3150OD3150R'))
    # tecan.firmware.send_command(
    #     Command(device, 'IP2000OD2000R'))

    liha.move_z_to_pos(750 + 300)
    tecan.firmware.send_command(
        Command(device, 'OP3150R'))

    liha.move_z_to_pos(700)

    liha.move_x_to_pos(2550 + 180)
    liha.move_z_to_pos(750)
    tecan.firmware.send_command(
        Command(device, 'OD3150R'))

    liha.move_z_to_pos(0)

    # tecan.firmware.send_command(
    #     Command(device, 'OV3600A0R'))

    # tecan.firmware.send_command(
    #     Command(device, 'BR'))

    # tecan.firmware.send_command(
    #     Command('O1', 'AFI', params=[1, 38, 8]))

    # tecan.firmware.send_command(
    #     Command(device, 'M6600IR'))  # M=Delay 3600ms I=Turns the valve drive to input port.

    # tecan.firmware.send_command(
    #     Command(device, 'IV3600P1500OA0R'))


if __name__ == '__main__':
    main()
