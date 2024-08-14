from tecan import Tecan, Firmware, LiHa


def main():
    tecan = Tecan(port='/dev/tty.usbserial-1110', firmware=Firmware.STANDARD)
    tecan.setup()

    liha = LiHa(tecan)
    liha.setup()

    # 1 ERROR
    # 2 OK
    # 3 ERROR
    # 4 ERROR
    # 5 ERROR
    # 6 ERROR
    # 7 ERROR
    # 8 ERROR

    liha.activate_single_tip(2)
    liha.wash_tips()


if __name__ == '__main__':
    main()
