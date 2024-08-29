from tecan import Tecan, Firmware, LiHa


def main():
    tecan = Tecan(port='/dev/tty.usbserial-110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()
    for tip in range(1, 9):

        # 1 ERROR
        # 2 OK
        # 3 ERROR
        # 4 ERROR
        # 5 ERROR
        # 6 ERROR
        # 7 ERROR
        # 8 ERROR

        try:
            liha.activate_single_tip(tip)
            liha.wash_tips(z_position=400)
            liha.move_z_to_pos(0)
            print(f'TIP {tip} OK')
        except Exception as e:
            print(f'TIP {tip} ERROR: {e}')

    liha.move_z_to_pos(0)


if __name__ == '__main__':
    main()
