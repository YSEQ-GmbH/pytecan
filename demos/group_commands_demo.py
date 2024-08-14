from tecan import Tecan, Firmware, LiHa


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    liha.activate_tip_range(1, 3)

    liha.wash_tips()

    liha.aspriate(volume=300, speed=5)

    liha.move_z_to_pos(0)

    liha.activate_tip_range(4, 6)

    liha.wash_tips()

    liha.move_z_to_pos(0)

    liha.activate_tip_range(1, 8)

    liha.wash_tips()

    liha.aspriate(volume=300, speed=1)
    liha.dispense(volume=300, speed=1)

    liha.aspriate(volume=300, speed=20)

    liha.activate_single_tip(1)

    liha.move_xyz_to_pos(x=2530, y=1390, z=750)

    liha.move_z_to_detect_liquid_and_submerge(
        z_start=750, z_max=1140, submerge_depth=10)

    liha.move_z_to_pos(0)
    liha.move_y_to_pos(0)

    # while True:
    #     tecan.firmware.read()
if __name__ == '__main__':
    main()
