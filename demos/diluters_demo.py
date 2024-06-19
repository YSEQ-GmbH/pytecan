from tecan import Tecan, Firmware, LiHa
from tecan.entities import Command


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    liha.move_y_to_pos(liha.actual_machine_y_range/2 - 350)
    liha.move_z_to_pos(650)

    # Initialize diluters
    for i in range(0, 8):

        device = f'D{i+1}'

        tecan.firmware.send_command(
            Command(device, 'YIP100OS9OD100R'))

    while True:
        for i in range(0, 8):
            device = f'D{i+1}'

            tecan.firmware.send_command(
                Command(device, 'OV3600A0R'))

            tecan.firmware.send_command(
                Command(device, 'BR'))

            tecan.firmware.send_command(
                Command('O1', 'AFI', params=[1, 38, 8]))

            tecan.firmware.send_command(
                Command(device, 'M500IR'))

            tecan.firmware.send_command(
                Command(device, 'IV3600P1500OA0R'))

        # tecan.firmware.send_command(
        #     Command('O1', 'AFI', params=[1, 38, 8]))

        input('Press Enter to continue...')


if __name__ == '__main__':
    main()
