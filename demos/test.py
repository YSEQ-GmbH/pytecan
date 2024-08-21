import time
from tecan import Tecan, Firmware, LiHa


class Config:
    # 50ul blue water per well to plate
    BLUE_WATER_VOLUME = 50

    # 80ul normal water per well to plate
    NORMAL_WATER_VOLUME = 80

    # 30ul air gap
    AIR_GAP_VOLUME = 30

    # Rows of tubes in the plate to be filled with liquid. MAX is 12 rows.
    ROWS = 3


def init() -> tuple[Tecan, LiHa]:
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    return tecan, liha


def fill_plate_with_blue_water(liha: LiHa, volume: int):
    for i in range(Config.ROWS):
        # Aspirate blue water, create an air gap before aspirating, and another air gap after aspirating
        liha.move_xyz_to_pos(x=1230, y=1100, z=700)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_detect_liquid_and_submerge(
            z_start=700, z_max=970, submerge_depth=10)
        liha.aspirate(volume=volume)
        liha.move_z_to_pos(700)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_pos(0)

        # Dispense blue water to plate with air gap before and after dispensing and touch wall
        row_x_pos = 5110 + (i * 90)
        liha.set_y_spacing(5)
        liha.move_xyz_to_pos(x=row_x_pos, y=1220, z=900)
        liha.dispense(volume=Config.AIR_GAP_VOLUME)
        liha.move_z_to_pos(920)
        liha.dispense(volume=volume)
        liha.move_z_to_pos(900)
        liha.dispense(volume=Config.AIR_GAP_VOLUME)

        # Touch wall
        liha.move_x_to_pos(row_x_pos - 23)
        liha.move_x_to_pos(row_x_pos)

        liha.move_z_to_pos(0)
        liha.set_y_spacing(0)


def remove_blue_water_to_waste(liha: LiHa, volume: int):
    for i in range(Config.ROWS):
        # Aspirate blue water, create an air gap before aspirating, and another air gap after aspirating
        row_x_pos = 5110 + (i * 90)
        liha.set_y_spacing(5)
        liha.move_xyz_to_pos(x=row_x_pos, y=2185, z=940)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_pos(1140, speed=400)
        liha.aspirate(volume=volume)

        liha.move_x_to_pos(row_x_pos + 5)
        for _ in range(3):
            liha.move_x_to_pos(row_x_pos - 10)
            liha.move_x_to_pos(row_x_pos + 10)
        liha.move_x_to_pos(row_x_pos)

        liha.move_z_to_pos(940)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_pos(0)
        liha.set_y_spacing(0)

        # Dispense blue water to waste with air gap before and after dispensing
        liha.move_xyz_to_pos(x=1230, y=2050, z=700)
        air = 50
        liha.dispense(volume=Config.AIR_GAP_VOLUME*2 + volume + air, speed=0)

        # Touch wall
        liha.move_z_to_pos(750)
        liha.move_x_to_pos(1230 - 90)
        liha.move_x_to_pos(1230)

        liha.aspirate(volume=air, speed=0)
        liha.move_z_to_pos(0)


def fill_plate_with_normal_water(liha: LiHa, volume: int):
    for i in range(Config.ROWS):
        # Aspirate normal water, create an air gap before aspirating, and another air gap after aspirating
        liha.move_xyz_to_pos(x=1230, y=150, z=700)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_detect_liquid_and_submerge(
            z_start=700, z_max=1580, submerge_depth=15)
        liha.aspirate(volume=volume)
        liha.move_z_to_pos(700)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_pos(0)

        # Dispense normal water to plate with air gap before and after dispensing and touch wall
        row_x_pos = 5110 + (i * 90)
        liha.set_y_spacing(5)
        liha.move_xyz_to_pos(x=row_x_pos, y=2185, z=960)
        liha.dispense(volume=Config.AIR_GAP_VOLUME)
        liha.move_z_to_pos(980)
        liha.dispense(volume=volume)
        liha.move_z_to_pos(960)
        liha.dispense(volume=Config.AIR_GAP_VOLUME)

        # Touch wall
        liha.move_x_to_pos(row_x_pos - 23)
        liha.move_x_to_pos(row_x_pos)

        liha.move_z_to_pos(0)
        liha.set_y_spacing(0)


def transfer_normal_water_to_different_plate(liha: LiHa, volume: int):
    input('Make sure water dose not have air bubbles. Press Enter to continue...')

    liha.set_y_spacing(5)

    for i in range(Config.ROWS):
        # Aspirate normal water from the plate on the magnet, create an air gap before aspirating, and another air gap after aspirating
        row_x_pos = 5110 + (i * 90)
        liha.move_xyz_to_pos(x=row_x_pos, y=2185, z=940)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_pos(1140, speed=400)
        liha.aspirate(volume=volume)

        liha.move_x_to_pos(row_x_pos + 5)
        for _ in range(3):
            liha.move_x_to_pos(row_x_pos - 10)
            liha.move_x_to_pos(row_x_pos + 10)
        liha.move_x_to_pos(row_x_pos)

        liha.move_z_to_pos(940)
        liha.aspirate(volume=Config.AIR_GAP_VOLUME, speed=1)
        liha.move_z_to_pos(0)

        # Dispense normal water to waste with air gap before and after dispensing
        liha.move_xyz_to_pos(x=row_x_pos, y=1220, z=900)
        liha.dispense(volume=Config.AIR_GAP_VOLUME)
        liha.move_z_to_pos(920)
        liha.dispense(volume=volume)
        liha.move_z_to_pos(900)
        liha.dispense(volume=Config.AIR_GAP_VOLUME)

        # Touch wall
        liha.move_x_to_pos(row_x_pos - 23)
        liha.move_x_to_pos(row_x_pos)

        liha.move_z_to_pos(0)
    liha.set_y_spacing(0)


def main():
    tecan, liha = init()

    # Wash tips
    liha.wash_tips()
    liha.aspirate(volume=300, speed=0)
    time.sleep(1)
    liha.dispense(volume=300, speed=0)
    liha.aspirate(volume=200, speed=1)
    liha.move_z_to_pos(0)

    # Fill plate with blue water
    fill_plate_with_blue_water(liha, volume=Config.BLUE_WATER_VOLUME)

    # Break and user prompt to move plate to magnet
    input('Move plate to magnet and put a new plate to transfer normal water to it. Press Enter to continue...')

    # Remove blue water to waste
    remove_blue_water_to_waste(liha, volume=Config.BLUE_WATER_VOLUME)

    # Wash tips

    liha.wash_tips()
    liha.aspirate(volume=300, speed=0)
    time.sleep(1)
    liha.dispense(volume=300, speed=0)
    liha.aspirate(volume=200, speed=1)
    liha.move_z_to_pos(0)

    # Fill plate with normal water
    fill_plate_with_normal_water(liha, volume=Config.NORMAL_WATER_VOLUME)

    # Transfer normal water to different plate (which is not on magnet)
    transfer_normal_water_to_different_plate(
        liha, volume=Config.NORMAL_WATER_VOLUME)

    # Wash tips
    liha.wash_tips()
    liha.move_z_to_pos(0)
    liha.move_y_to_pos(0)

    # Close connection
    tecan.close()


if __name__ == '__main__':
    main()
