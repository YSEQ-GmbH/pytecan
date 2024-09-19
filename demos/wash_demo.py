from tecan import Tecan, Firmware, LiHa


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    liha.activate_tip_range(1, 4)

    while True:
        liha.wash_tips(x_position=20, y_position=1000, z_position=750)
        liha.move_z_to_pos(0)

        should_continue = input('Continue? (y/n): ')

        if should_continue.lower() != 'y':
            break

    tecan.close()


if __name__ == '__main__':
    main()
