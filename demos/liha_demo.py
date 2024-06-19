from tecan import Tecan, Firmware, LiHa


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    # Test X-axis
    liha.move_x_to_pos(1000)
    liha.move_x_to_pos(0)

    # Test Y-axis
    liha.move_y_to_pos(1000)
    liha.move_y_to_pos(0)

    liha.set_y_spacing(100)
    liha.move_y_to_pos(1000)

    liha.set_y_spacing(0)
    liha.move_y_to_pos(0)

    # Test Z-axis
    liha.activate_tip_range(1, 4)
    liha.move_z_to_pos(700)
    liha.move_z_to_pos(0)

    liha.activate_tip_range(5, 8)
    liha.move_z_to_pos(700)
    liha.move_z_to_pos(0)

    for i in range(1, 9):
        liha.activate_single_tip(i)
        liha.move_z_to_pos(700)
        liha.move_z_to_pos(0)


if __name__ == '__main__':
    main()
