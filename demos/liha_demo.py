import time
from tecan import Tecan, Firmware, LiHa


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    while True:
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
        liha.set_active_tips_status(6, 8, False)
        liha.move_z_to_pos(700)

        liha.move_z_to_pos(0)

        liha.set_active_tips_status(1, 8, True)
        liha.move_z_to_pos(700)

        liha.move_z_to_pos(0)

        time.sleep(5)


if __name__ == '__main__':
    main()


#    resources = {
#         'deck': {
#             'x_range': liha.actual_machine_x_range - 86,
#             'y_range': liha.actual_machine_y_range,
#             'z_range': 1650,
#             'location': {
#                 'x': 0,
#                 'y': 0,
#             },
#             'rows': 69,
#         }
#     }

    # z_position = resources['deck']['z_range']

    # z_position = liha.actual_machine_z_range - z_position
    # tecan.firmware.send_command(
    #     Command('A1', f"PAZ{','.join([str(z_position)]*8)}"))

    # time.sleep(0.5)

    # rows = resources['deck']['rows']-1
    # for i in range(0, rows):
    #     target_x_position = (
    #         (i+1)*(resources['deck']['x_range'])//rows)

    #     liha.move_x_to_pos(target_x_position)
    #     current_x_position = liha.report_current_x_position()

    #     print(f'Current x position: {current_x_position} {target_x_position}')
    #     time.sleep(0.5)
