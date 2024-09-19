from tecan import Tecan, Firmware, LiHa


class Config:
    COLUMNS = 12
    AIR_GAP_BEFORE = 30
    AIR_GAP_AFTER = 30

    WASH_XYZ_POS = (x := 30, y := 150, z := 900)

    B4_XYZ_POS = (x := 5980, y := 1075, z := 700)
    B4_Z_START_LIQUID_DETECTION = 700
    B4_Z_MAX_LIQUID_DETECTION = 970

    B3_XYZ_POS = (x := 4600, y := 1075, z := 770)
    B3_SPACE_BETWEEN_COLUMNS = 90
    B3_Y_SPACING = 6
    B3_SPACE_BETWEEN_TIP_AND_WALL = 33
    B3_Z_START_LIQUID_DETECTION = 770
    B3_Z_MAX_LIQUID_DETECTION = 1040

    C3_XYZ_POS = (x := 4600, y := 2040, z := 860)
    C3_SPACE_BETWEEN_COLUMNS = 90
    C3_Y_SPACING = 6
    C3_SPACE_BETWEEN_TIP_AND_WALL = 25
    C3_Z_START_LIQUID_DETECTION = 860
    C3_Z_MAX_LIQUID_DETECTION = 1030

    A1_XYZ_POS = (x := 330, y := -70, z := 800)
    A1_SPACE_BETWEEN_COLUMNS = 90
    A1_Y_SPACING = 6
    A1_SPACE_BETWEEN_TIP_AND_WALL = 33
    A1_Z_START_LIQUID_DETECTION = 800
    A1_Z_MAX_LIQUID_DETECTION = 1080

    A3_XYZ_POS = (x := 4550, y := 150, z := 570)
    A3_SPACE_BETWEEN_TIP_AND_WALL = 60

    A5_XYZ_POS = (x := 6475, y := 1400, z := 550)
    A5_MINUS_Y_FOR_TIP_2_4_6_8 = 200
    A5_Y_SPACING = 130
    A5_Z_START_LIQUID_DETECTION = 550
    A5_Z_MAX_LIQUID_DETECTION = 1655

    A6_XYZ_POS = (x := 7000, y := 1400, z := 550)
    A6_MINUS_Y_FOR_TIP_2_4_6_8 = 200
    A6_Y_SPACING = 130
    A6_Z_START_LIQUID_DETECTION = 550
    A6_Z_MAX_LIQUID_DETECTION = 1655

    B2_XYZ_POS = (x := 330, y := 890, z := 910)
    B2_SPACE_BETWEEN_COLUMNS = 90
    B2_Y_SPACING = 6
    B2_SPACE_BETWEEN_TIP_AND_WALL = 25


def main():
    tecan, liha = init()

    wash_tips(liha)
    input('\nFill trough B4 with 4 uL of beads. Open lids of LowTE. Put sample plate on C3. Put DWP on B3. Press Enter to continue...')
    fill_dwp_with_lowte_off_magnet(liha, volume=16)
    fill_dwp_with_beads(liha, volume=15)
    wash_tips(liha)
    transfer_samples_to_dwp(liha)
    input('\nLeave DWP to incubate for 10mins off the magnet (e.g. at D1). Place DWP on magnet (A1). Put new DWP to B3. Press Enter to continue...')
    fill_dwp_with_beads(liha, volume=7.5)
    transfer_liquid_to_new_dwp(liha, volume=65)
    input('\nLeave DWP to incubate for 10mins off the magnet (e.g. at D1). Place DWP on magnet (A1). Open lids of EtOH tubes. Press Enter to continue...')
    remove_all_liquid_from_dwp(liha, volume=75)
    fill_dwp_with_etoh(liha, volume=600)
    remove_all_liquid_from_dwp(liha, volume=600)
    fill_dwp_with_etoh(liha, volume=600)
    remove_all_liquid_from_dwp(liha, volume=600)
    countdown_clock(300)
    fill_dwp_with_lowte(liha, volume=10.5)
    input('Vortex DWP (A1). Rest DWP (A1) for 5mins off the magnet (e.g. at D1). Place new micro plate on C3. Put DWP off magnet to B3. Press Enter to continue...')
    transfer_liquid_to_new_plate(liha, volume=15)

    print('Done!')

    tecan.close()


def init() -> tuple[Tecan, LiHa]:
    tecan = Tecan(port='/dev/ttyUSB0', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    return tecan, liha


def wash_tips(liha: LiHa):
    liha.set_y_spacing(6)

    liha.wash_tips(*Config.WASH_XYZ_POS)
    liha.move_z_to_pos(0)
    liha.aspirate(volume=250)

    liha.set_y_spacing(0)


def handle_liquid_detection_error(liha: LiHa, z_start: int, z_max: int, submerge_depth: int):
    while True:
        try:
            liha.move_z_to_detect_liquid_and_submerge(
                z_start=z_start, z_max=z_max, submerge_depth=submerge_depth)
            break
        except Exception as e:
            liha.move_z_to_pos(0)
            print(f'ERROR: {e}')
            print('click Enter to retry or Ctrl+C to exit...')
            liha.move_z_to_pos(z_start)


def fill_dwp_with_beads(liha: LiHa, volume: int = 15):
    for i in range(Config.COLUMNS):
        # Aspirate beads
        liha.set_y_spacing(0)
        liha.move_xyz_to_pos(*Config.B4_XYZ_POS)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        liha.move_z_to_pos(Config.B4_Z_MAX_LIQUID_DETECTION, speed=400)
        liha.aspirate(volume=volume, speed=20)
        liha.move_z_to_pos(Config.B4_Z_START_LIQUID_DETECTION)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        # Dispense beads
        liha.set_y_spacing(Config.B3_Y_SPACING)
        x, y, z = Config.B3_XYZ_POS
        x += i * Config.B3_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.dispense(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(z + 20, speed=400)
        liha.dispense(volume=volume, speed=20)
        liha.move_z_to_pos(z)
        liha.dispense(volume=Config.AIR_GAP_BEFORE)

        # Touch wall
        liha.move_x_to_pos(x - Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x + Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)

    liha.set_y_spacing(0)


def transfer_samples_to_dwp(liha: LiHa):
    for i in range(Config.COLUMNS):
        # Aspirate samples
        liha.set_y_spacing(Config.C3_Y_SPACING)
        x, y, z = Config.C3_XYZ_POS
        x += i * Config.C3_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        liha.move_z_to_pos(Config.C3_Z_MAX_LIQUID_DETECTION, speed=400)

        # Move while aspirating to aspirate everything from the well
        liha.aspirate(volume=53)
        for _ in range(5):
            liha.move_x_to_pos(x - 10)
            liha.move_z_to_pos(
                Config.C3_Z_MAX_LIQUID_DETECTION - (i + 1), speed=400)
            liha.move_x_to_pos(x + 10)

        liha.move_z_to_pos(z)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        # Dispense samples
        liha.set_y_spacing(Config.B3_Y_SPACING)
        x, y, z = Config.B3_XYZ_POS
        x += i * Config.B3_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.dispense(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(z + 20, speed=400)
        liha.dispense(volume=53 + Config.AIR_GAP_BEFORE)

        # Mix samples
        liha.move_z_to_pos(Config.B3_Z_MAX_LIQUID_DETECTION - 20, speed=400)
        for _ in range(10):
            liha.aspirate(volume=60)
            liha.dispense(volume=60)
        liha.move_z_to_pos(z)

        # Touch wall
        liha.move_x_to_pos(x - Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x + Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)

        wash_tips(liha)

    liha.set_y_spacing(0)


def countdown_clock(seconds: int):
    import time
    for i in range(seconds, 0, -1):
        mins, secs = divmod(i, 60)
        time_format = f'{mins} minutes {secs} seconds left...' if mins > 0 else f'{secs} seconds left...'
        print(f'\r{time_format}', end='', flush=True)
        time.sleep(1)
    print('\rCountdown finished!')


def remove_all_liquid_from_dwp(liha: LiHa, volume: int = 100):
    for i in range(Config.COLUMNS):
        # Aspirate liquid
        liha.set_y_spacing(Config.A1_Y_SPACING)
        x, y, z = Config.A1_XYZ_POS
        x += i * Config.A1_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        liha.move_z_to_pos(Config.A1_Z_MAX_LIQUID_DETECTION - 10, speed=400)
        liha.aspirate(volume=volume, speed=20)
        liha.move_z_to_pos(z)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(0)

        # Dispense liquid to trash
        liha.set_y_spacing(0)
        x, y, z = Config.A3_XYZ_POS
        liha.move_xyz_to_pos(x, y, z)
        liha.dispense(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(z + 20, speed=400)
        liha.dispense(volume=volume)
        liha.move_z_to_pos(z)
        liha.dispense(volume=Config.AIR_GAP_BEFORE)

        # Touch wall
        liha.move_x_to_pos(x - Config.A3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)

        # Wash tips
        wash_tips(liha)

    liha.set_y_spacing(0)


def fill_dwp_with_etoh(liha: LiHa, volume: int = 600):
    for i in range(Config.COLUMNS):
        # Aspirate EtOH
        liha.set_y_spacing(Config.A5_Y_SPACING)

        x, y, z = Config.A5_XYZ_POS

        # Fill first 4 tips
        liha.activate_tip_custom([1, 3, 5, 7])
        liha.move_xyz_to_pos(x, y, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        handle_liquid_detection_error(
            liha=liha,
            z_start=Config.A5_Z_START_LIQUID_DETECTION,
            z_max=Config.A5_Z_MAX_LIQUID_DETECTION,
            submerge_depth=30
        )
        liha.aspirate(volume=volume, speed=15)
        liha.move_z_to_pos(Config.A5_Z_START_LIQUID_DETECTION)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        # Fill last 4 tips
        liha.activate_tip_custom([2, 4, 6, 8])
        liha.move_xyz_to_pos(x, y - Config.A5_MINUS_Y_FOR_TIP_2_4_6_8, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        handle_liquid_detection_error(
            liha=liha,
            z_start=Config.A5_Z_START_LIQUID_DETECTION,
            z_max=Config.A5_Z_MAX_LIQUID_DETECTION,
            submerge_depth=30
        )
        liha.aspirate(volume=volume, speed=15)
        liha.move_z_to_pos(Config.A5_Z_START_LIQUID_DETECTION)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        liha.move_z_to_pos(0)
        liha.activate_all_tips()

        # Dispense EtOH
        liha.set_y_spacing(Config.A1_Y_SPACING)
        x, y, z = Config.A1_XYZ_POS
        x += i * Config.A1_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.dispense(volume=Config.AIR_GAP_AFTER + volume +
                      Config.AIR_GAP_BEFORE, speed=20)
        liha.move_z_to_pos(0)

    liha.set_y_spacing(0)


def fill_dwp_with_lowte(liha: LiHa, volume: int = 11):
    for i in range(Config.COLUMNS):
        # Aspirate LowTE
        liha.set_y_spacing(Config.A6_Y_SPACING)

        x, y, z = Config.A6_XYZ_POS

        # Fill first 4 tips
        liha.activate_tip_custom([1, 3, 5, 7])
        liha.move_xyz_to_pos(x, y, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        handle_liquid_detection_error(
            liha=liha,
            z_start=Config.A6_Z_START_LIQUID_DETECTION,
            z_max=Config.A6_Z_MAX_LIQUID_DETECTION,
            submerge_depth=30
        )
        liha.aspirate(volume=volume, speed=15)
        liha.move_z_to_pos(Config.A6_Z_START_LIQUID_DETECTION)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        # Fill last 4 tips
        liha.activate_tip_custom([2, 4, 6, 8])
        liha.move_xyz_to_pos(x, y - Config.A6_MINUS_Y_FOR_TIP_2_4_6_8, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        handle_liquid_detection_error(
            liha=liha,
            z_start=Config.A6_Z_START_LIQUID_DETECTION,
            z_max=Config.A6_Z_MAX_LIQUID_DETECTION,
            submerge_depth=30
        )
        liha.aspirate(volume=volume, speed=15)
        liha.move_z_to_pos(Config.A6_Z_START_LIQUID_DETECTION)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        liha.move_z_to_pos(0)
        liha.activate_all_tips()

        # Dispense LowTE
        liha.set_y_spacing(Config.A1_Y_SPACING)
        x, y, z = Config.A1_XYZ_POS
        x += i * Config.A1_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.dispense(volume=Config.AIR_GAP_AFTER + volume +
                      Config.AIR_GAP_BEFORE, speed=15)

        # Touch wall
        liha.move_x_to_pos(x + Config.A1_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x - Config.A1_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)

        # Wash tips
        wash_tips(liha)

    liha.set_y_spacing(0)
    x, y, _ = Config.WASH_XYZ_POS
    liha.move_xyz_to_pos(
        x=x, y=y, z=0,
    )


def fill_dwp_with_lowte_off_magnet(liha: LiHa, volume: int = 11):
    for i in range(Config.COLUMNS):
        # Aspirate LowTE
        liha.set_y_spacing(Config.A6_Y_SPACING)

        x, y, z = Config.A6_XYZ_POS

        # Fill first 4 tips
        liha.activate_tip_custom([1, 3, 5, 7])
        liha.move_xyz_to_pos(x, y, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        handle_liquid_detection_error(
            liha=liha,
            z_start=Config.A6_Z_START_LIQUID_DETECTION,
            z_max=Config.A6_Z_MAX_LIQUID_DETECTION,
            submerge_depth=30
        )
        liha.aspirate(volume=volume, speed=15)
        liha.move_z_to_pos(Config.A6_Z_START_LIQUID_DETECTION)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        # Fill last 4 tips
        liha.activate_tip_custom([2, 4, 6, 8])
        liha.move_xyz_to_pos(x, y - Config.A6_MINUS_Y_FOR_TIP_2_4_6_8, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        handle_liquid_detection_error(
            liha=liha,
            z_start=Config.A6_Z_START_LIQUID_DETECTION,
            z_max=Config.A6_Z_MAX_LIQUID_DETECTION,
            submerge_depth=30
        )
        liha.aspirate(volume=volume, speed=15)
        liha.move_z_to_pos(Config.A6_Z_START_LIQUID_DETECTION)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)

        liha.move_z_to_pos(0)
        liha.activate_all_tips()

        # Dispense LowTE
        liha.set_y_spacing(Config.B3_Y_SPACING)
        x, y, z = Config.B3_XYZ_POS
        x += i * Config.B3_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.move_z_to_pos(Config.B3_Z_MAX_LIQUID_DETECTION - 40)
        liha.dispense(volume=Config.AIR_GAP_AFTER + volume +
                      Config.AIR_GAP_BEFORE, speed=15)

        # Touch wall
        liha.move_x_to_pos(x + Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x - Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)

    # Wash tips
    wash_tips(liha)

    liha.set_y_spacing(0)
    x, y, _ = Config.WASH_XYZ_POS
    liha.move_xyz_to_pos(
        x=x, y=y, z=0,
    )


def transfer_liquid_to_new_plate(liha: LiHa, volume: int = 11):
    for i in range(Config.COLUMNS):
        # Aspirate liquid
        liha.set_y_spacing(Config.B3_Y_SPACING)
        x, y, z = Config.B3_XYZ_POS
        x += i * Config.B3_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        liha.move_z_to_pos(Config.B3_Z_MAX_LIQUID_DETECTION, speed=400)
        liha.aspirate(volume=volume, speed=20)
        for _ in range(5):
            liha.move_x_to_pos(x - 10)
            liha.move_z_to_pos(
                Config.B3_Z_MAX_LIQUID_DETECTION - (i + 1), speed=400)
            liha.move_x_to_pos(x + 10)
        liha.move_z_to_pos(z)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(0)

        # Dispense liquid to new plate
        liha.set_y_spacing(Config.C3_Y_SPACING)
        x, y, z = Config.C3_XYZ_POS
        x += i * Config.C3_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.dispense(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(z + 20, speed=400)
        liha.dispense(volume=volume)
        liha.move_z_to_pos(z)
        liha.dispense(volume=Config.AIR_GAP_BEFORE)

        # Touch wall
        liha.move_x_to_pos(x + Config.C3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x - Config.C3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)

        wash_tips(liha)

    liha.set_y_spacing(0)


def transfer_liquid_to_new_dwp(liha: LiHa, volume: int = 65):
    for i in range(Config.COLUMNS):
        # Aspirate liquid
        liha.set_y_spacing(Config.A1_Y_SPACING)
        x, y, z = Config.A1_XYZ_POS
        x += i * Config.A1_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.aspirate(volume=Config.AIR_GAP_BEFORE)
        liha.move_z_to_pos(Config.A1_Z_MAX_LIQUID_DETECTION - 5, speed=400)
        liha.aspirate(volume=volume, speed=20)
        for _ in range(5):
            liha.move_x_to_pos(x - 10)
            liha.move_z_to_pos(
                Config.A1_Z_MAX_LIQUID_DETECTION - (i + 1), speed=400)
            liha.move_x_to_pos(x + 10)

        liha.move_z_to_pos(z)
        liha.aspirate(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(0)

        # Dispense liquid to new plate
        liha.set_y_spacing(Config.B3_Y_SPACING)
        x, y, z = Config.B3_XYZ_POS
        x += i * Config.B3_SPACE_BETWEEN_COLUMNS
        liha.move_xyz_to_pos(x, y, z)
        liha.dispense(volume=Config.AIR_GAP_AFTER)
        liha.move_z_to_pos(z + 20, speed=400)
        liha.dispense(volume=volume)
        liha.move_z_to_pos(z)
        liha.dispense(volume=Config.AIR_GAP_BEFORE)

        # Mix samples
        liha.move_z_to_pos(Config.B3_Z_MAX_LIQUID_DETECTION - 20, speed=400)
        for _ in range(10):
            liha.aspirate(volume=60)
            liha.dispense(volume=60)
        liha.move_z_to_pos(z)

        # Touch wall
        liha.move_x_to_pos(x - Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x + Config.B3_SPACE_BETWEEN_TIP_AND_WALL)
        liha.move_x_to_pos(x)

        liha.move_z_to_pos(0)

        wash_tips(liha)

    liha.set_y_spacing(0)


if __name__ == '__main__':
    main()
