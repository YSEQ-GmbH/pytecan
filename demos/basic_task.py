from tecan import Tecan, Firmware, LiHa
from tecan.entities import Command


def group_command(tecan: Tecan, cmd: str):
    group_channel = 'G'

    tecan.firmware.send_commands(
        [Command(f'D{i}', cmd) for i in range(1, 9)], group_channel=group_channel)

    print()


def aspirate(tecan: Tecan, volume: int = 0, speed: int = 9, device='D1'):
    volume = int(volume * 3.15)
    if volume > 3150:
        raise Exception('Volume too high')

    tecan.firmware.send_command(command=Command(
        device, f'S{speed}OP{volume}R'))


def aspirate_air_gap(tecan: Tecan, speed: int = 9, device='D1'):
    aspirate(tecan, volume=30, speed=speed, device=device)


def dispense(tecan: Tecan, volume: int = 0, speed: int = 9, device='D1'):
    volume = int(volume * 3.15)
    if volume > 3150:
        raise Exception('Volume too high')

    tecan.firmware.send_command(command=Command(
        device, f'S{speed}OD{volume}R'))


def dispense_air_gap(tecan: Tecan, speed: int = 9, device='D1'):
    dispense(tecan, volume=30, speed=speed, device=device)


def wash_tips(liha: LiHa, tecan: Tecan):
    liha.move_x_to_pos(0)
    liha.move_y_to_pos(liha.actual_machine_y_range/2 - 350)
    liha.move_z_to_pos(700)

    group_command(tecan, 'YIP100OS9OD100R')
    group_command(tecan, 'OV3600A0R')
    group_command(tecan, 'BR')

    tecan.firmware.send_command(
        command=Command('O1', 'AFI', params=[1, 38, 18]))

    group_command(tecan, 'M500IR')
    group_command(tecan, 'IV3600P1500OA0R')

    # Air gap
    liha.aspriate(volume=300, speed=5)

    liha.move_z_to_pos(0)


def calculate_tip_select(tips):
    """
    Calculate the TipSelect value for the given list of tips.

    Args:
    tips (list of int): List of tip numbers to be selected (e.g., [2, 4, 6, 8]).

    Returns:
    int: The calculated TipSelect value.
    """
    tip_select = 0
    for tip in tips:
        # Set the corresponding bit for each tip number
        tip_select |= 1 << (tip - 1)
    return tip_select


def liquid_detection(liha: LiHa, tecan: Tecan,  z_start: int, z_max: int, submerge_depth=10,):
    z_start = liha.actual_machine_z_range - z_start
    z_max = liha.actual_machine_z_range - z_max

    active_tips = [i+1 for i, tip in enumerate(liha.active_tips_status) if tip]

    tecan.firmware.send_command(
        command=Command('A1', 'MDT', params=[calculate_tip_select(active_tips), submerge_depth, z_start,  z_max]))


def fill_tips_with_liquid(liha: LiHa, tecan: Tecan, volume: int = 9):
    # x=2530, y=1385, z=1140, padding=83

    max_depth = 1140

    for i, tip in enumerate(liha.active_tips_status):
        device = f'D{i+1}'
        if tip:
            liha.activate_single_tip(i+1)
            liha.move_xyz_to_pos(x=2530, y=1385 - (83 * i), z=700)

            aspirate_air_gap(tecan, speed=9, device=device)

            # move z axis until the tip touches the liquid and then submerge 10mm
            liquid_detection(liha, tecan, z_start=700,
                             z_max=max_depth, submerge_depth=10)

            aspirate(tecan, volume=volume, speed=9, device=device)

            liha.move_z_to_pos(700, speed=400)

            aspirate_air_gap(tecan, speed=9, device=device)

    liha.activate_tip_range(1, 8)
    liha.move_z_to_pos(0)


def dispense_liquid_from_tips(liha: LiHa, tecan: Tecan, volume: int = 9, x_pos=0):
    # x=5110,y=1220, z=1000, padding=90, touch_wall=23

    liha.set_y_spacing(5)

    full_x_pos = 5110 + x_pos

    liha.move_xyz_to_pos(x=full_x_pos, y=1220, z=920)

    liha.dispense(volume=30)
    # for i, tip in enumerate(liha.active_tips_status):
    #     device = f'D{i+1}'
    #     if tip:
    #         dispense_air_gap(tecan, speed=9, device=device)

    liha.move_z_to_pos(960, speed=400)

    liha.dispense(volume=volume)
    # for i, tip in enumerate(liha.active_tips_status):
    #     device = f'D{i+1}'
    #     if tip:
    #         dispense(tecan, volume=volume, speed=9, device=device)

    liha.move_z_to_pos(920, speed=400)

    liha.dispense(volume=30)
    # for i, tip in enumerate(liha.active_tips_status):
    #     device = f'D{i+1}'
    #     if tip:
    #         dispense_air_gap(tecan, speed=9, device=device)

    # touch wall
    liha.move_x_to_pos(full_x_pos - 23)
    liha.move_x_to_pos(full_x_pos)

    liha.move_z_to_pos(800, speed=400)
    liha.move_z_to_pos(0)
    liha.set_y_spacing(0)


def main():
    # This is the volume of liquid to be aspirated and dispensed in microliters
    volume = 10

    # This is the number of rows of tubes in the plate to be filled with liquid. MAX is 12 rows.
    rows = 6

    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    wash_tips(liha, tecan)

    for i in range(rows):
        fill_tips_with_liquid(liha, tecan, volume=volume)
        dispense_liquid_from_tips(liha, tecan, volume=volume, x_pos=90*i)

    wash_tips(liha, tecan)

    tecan.close()


if __name__ == '__main__':
    main()
