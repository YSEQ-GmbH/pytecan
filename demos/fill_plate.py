from tecan import Tecan, Firmware, LiHa


class Config:
    AIR_GAP_VOLUME = 30

    TUBE_XYZ_POS = (x := 1940, y := 2020, z := 700)
    TUBE_START_Z = 700
    TUBE_MAX_Z = 1140
    TUBE_SPACING_Y_TIPS = 85

    C1_XYZ_POS = (x := 350, y := 1840, z := 890)
    C1_START_Z = 890
    C1_MAX_Z = 970
    C1_SPACING_BETWEEN_COLUMNS = 90


def main():
    tecan, liha = init()

    liha.wash_tips()
    liha.aspirate(volume=100, speed=1)

    wells = int(input('Enter number of wells you need to fill: '))
    volume = int(input('Enter volume to dispense in each well: '))

    columns = wells // 8
    remainder = wells % 8

    for column in range(columns + 1):
        wells = 8
        if column == columns:
            if remainder == 0:
                break
            wells = remainder

        # Fill tips
        for tip in range(1, wells + 1):
            liha.activate_single_tip(tip)
            x, y, z = Config.TUBE_XYZ_POS
            y -= Config.TUBE_SPACING_Y_TIPS * (tip - 1)
            liha.move_xyz_to_pos(x=x, y=y, z=z)
            liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)

            try:
                liha.move_z_to_detect_liquid_and_submerge(
                    z_start=Config.TUBE_START_Z, z_max=Config.TUBE_MAX_Z, submerge_depth=10)
            except Exception:
                liha.move_z_to_pos(Config.TUBE_MAX_Z, speed=400)

            liha.aspirate(volume=volume)

            liha.move_z_to_pos(Config.TUBE_START_Z, speed=400)
            liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
            liha.move_z_to_pos(0)

        # Dispense
        x, y, z = Config.C1_XYZ_POS
        x += Config.C1_SPACING_BETWEEN_COLUMNS * column
        liha.set_y_spacing(6)
        liha.activate_tip_range(1, wells)
        liha.move_xyz_to_pos(x=x, y=y, z=z + 20)
        liha.dispense(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.dispense(volume=volume)
        liha.move_z_to_pos(z + 15)
        liha.dispense(volume=Config.AIR_GAP_VOLUME, speed=1)

        # Touch wall
        liha.move_x_to_pos(x + 25)
        liha.move_x_to_pos(x - 25)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)
        liha.set_y_spacing(0)

    liha.activate_all_tips()
    liha.wash_tips()
    tecan.close()


def init() -> tuple[Tecan, LiHa]:
    tecan = Tecan(port='/dev/tty.usbserial-1110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    return tecan, liha


if __name__ == '__main__':
    main()
