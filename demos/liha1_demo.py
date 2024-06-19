from tecan import Tecan, Firmware, LiHa


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    liha.move_y_to_pos(1900)
    liha.move_x_to_pos(1200)
    liha.move_z_to_pos(700)
    liha.activate_single_tip(1)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1810)
    liha.activate_single_tip(2)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1720)
    liha.activate_single_tip(3)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1630)
    liha.activate_single_tip(4)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1540)
    liha.activate_single_tip(5)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1450)
    liha.activate_single_tip(6)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1360)
    liha.activate_single_tip(7)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1270)
    liha.activate_single_tip(8)
    liha.move_z_to_pos(1000)
    liha.move_z_to_pos(700)
    liha.move_y_to_pos(1180)

    liha.move_x_to_pos(2570)
    liha.set_y_spacing(90)
    liha.move_y_to_pos(1380)
    liha.activate_tip_range(1, 4)
    liha.move_z_to_pos(850)
    liha.move_z_to_pos(700)
    liha.move_x_to_pos(2750)
    liha.move_y_to_pos(660)
    liha.activate_tip_range(5, 8)
    liha.move_z_to_pos(850)
    liha.move_z_to_pos(700)


if __name__ == '__main__':
    main()
