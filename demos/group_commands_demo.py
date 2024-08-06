from tecan import Tecan, Firmware, LiHa
from tecan.entities import Command


def wash_tips(liha: LiHa, tecan: Tecan):
    liha.move_x_to_pos(0)
    liha.move_y_to_pos(liha.actual_machine_y_range/2 - 350)
    liha.move_z_to_pos(700)

    group_command(tecan, 'YIP100OS9OD100R')
    group_command(tecan, 'OV3600A0R')
    group_command(tecan, 'BR')

    tecan.firmware.send_command(
        command=Command('O1', 'AFI', params=[1, 38, 8]))

    group_command(tecan, 'M500IR')
    group_command(tecan, 'IV3600P1500OA0R')

    # Air gap
    liha.aspriate(volume=300, speed=5)
    liha.dispense(volume=300, speed=5)
    liha.aspriate(volume=300, speed=10)
    liha.dispense(volume=300, speed=10)
    liha.aspriate(volume=300, speed=5)

    liha.move_z_to_pos(0)


def group_command(tecan: Tecan, cmd: str):
    group_channel = 'G'

    tecan.firmware.send_commands(
        [Command(f'D{i}', cmd) for i in range(1, 9)], group_channel=group_channel)

    print()


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    wash_tips(liha, tecan)

    while True:
        tecan.firmware.read()


if __name__ == '__main__':
    main()
