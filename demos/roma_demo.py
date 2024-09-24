from tecan import Tecan, Firmware, Roma


def main():
    tecan = Tecan(port='/dev/ttyUSB0', firmware=Firmware.STANDARD)
    tecan.setup()

    roma = Roma(tecan)
    roma.setup()

    input('Please put DWP plate at position 5 and press enter to continue')

    roma.move_y_to_pos(1000)
    roma.move_x_to_pos(4400)
    roma.rotate_to_degree(180)
    roma.move_z_to_pos(700)
    roma.move_g_to_pos(900)
    roma.move_y_to_pos(300)

    roma.move_g_to_pos(730)

    roma.move_z_to_pos(500)
    roma.move_y_to_pos(2000)
    roma.move_x_to_pos(9600)
    roma.move_y_to_pos(420)
    roma.move_z_to_pos(690)
    roma.move_y_to_pos(300)

    roma.move_g_to_pos(900)

    roma.move_z_to_pos(200)
    roma.move_y_to_pos(1300)
    roma.move_g_to_pos(550)

    roma.move_x_to_pos(2000)
    roma.rotate_to_degree(0)
    roma.move_z_to_pos(0)
    roma.move_y_to_pos(0)


if __name__ == '__main__':
    main()
