from tecan import Tecan, Firmware, LiHa
from tecan.entities import Command, Request, Response


def dispense_liquid(tecan: Tecan, volume: int = 0, speed: int = 9):
    volume = int(volume * 3.15)
    if volume > 3150:
        # Split the volume into multiple dispenses until the total volume is dispensed
        while volume > 3150:
            tecan.firmware.send_command(command=Command(
                'D1', f'S{speed}IP3150OD3150R'))
            volume -= 3150

    tecan.firmware.send_command(command=Command(
        'D1', f'S{speed}IP{volume}OD{volume}R'))


def aspirate(tecan: Tecan, volume: int = 0, speed: int = 9):
    volume = int(volume * 3.15)
    if volume > 3150:
        raise Exception('Volume too high')

    tecan.firmware.send_command(command=Command(
        'D1', f'S{speed}OP{volume}R'))


def dispense(tecan: Tecan, volume: int = 0, speed: int = 9):
    volume = int(volume * 3.15)
    if volume > 3150:
        raise Exception('Volume too high')

    tecan.firmware.send_command(command=Command(
        'D1', f'S{speed}OD{volume}R'))


def wash_tips(liha: LiHa, tecan: Tecan):
    liha.move_x_to_pos(0)
    liha.move_y_to_pos(liha.actual_machine_y_range/2 - 350)
    liha.move_z_to_pos(700)

    # Initialize diluter
    tecan.firmware.send_command(command=Command('D1', 'YIP100OS9OD100R'))

    tecan.firmware.send_command(command=Command('D1', 'OV3600A0R'))
    tecan.firmware.send_command(command=Command('D1', 'BR'))
    tecan.firmware.send_command(
        command=Command('O1', 'AFI', params=[1, 38, 8]))
    tecan.firmware.send_command(command=Command('D1', 'M500IR'))
    tecan.firmware.send_command(command=Command('D1', 'IV3600P1500OA0R'))

    liha.move_z_to_pos(0)
    aspirate(tecan, volume=200, speed=9)


def fill_tube(liha: LiHa, tecan: Tecan):
    liha.move_x_to_pos(2550)
    liha.move_y_to_pos(1380)
    liha.move_z_to_pos(800)

    dispense_liquid(tecan, volume=1500, speed=9)

    liha.move_z_to_pos(0)


def aspirate_20ul(liha: LiHa, tecan: Tecan):
    liha.move_x_to_pos(2550)
    liha.move_y_to_pos(1380)
    liha.move_z_to_pos(1140)

    aspirate(tecan, volume=20, speed=9)

    liha.move_z_to_pos(0)

    # Air gap
    aspirate(tecan, volume=20, speed=9)


def dispense_20ul(liha: LiHa, tecan: Tecan, x_pos=0):
    liha.move_x_to_pos(5100 + 25 + x_pos)
    liha.move_y_to_pos(1200 + 10)

    # Air gap
    dispense(tecan, volume=20, speed=9)

    liha.move_z_to_pos(950)

    dispense(tecan, volume=20, speed=9)

    liha.move_z_to_pos(0)


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    liha.activate_single_tip(1)

    wash_tips(liha, tecan)

    # # fill_tube(liha, tecan)

    for i in range(12):
        aspirate_20ul(liha, tecan)
        dispense_20ul(liha, tecan, x_pos=i*90)

    wash_tips(liha, tecan)


if __name__ == '__main__':
    main()
