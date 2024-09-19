import serial
from tecan.entities import Command
from tecan.firmware.standard import Standard


def init():
    usb_serial = serial.Serial(
        port='/dev/tty.usbserial-1110',
        baudrate=9600,
        timeout=60*5,
        writeTimeout=5,
        interCharTimeout=10
    )

    return Standard(usb_serial)


def main():
    firmware = init()

    respone = firmware.send_command(
        Command('A1', 'RGZ', ))
    print(respone.content_str)

    while True:
        firmware.read()


if __name__ == '__main__':
    main()

# EQUAL: 1155

# TIP 1: 1168 -> 13
# TIP 2: 1155 -> 0
# TIP 3: 1165 -> 10
# TIP 4: 1156 -> 1
# TIP 5: 1167 -> 12
# TIP 6: 1156 -> 1
# TIP 7: 1166 -> 11
# TIP 8: 1161 -> 6

# Command('A1', 'SOZ', params=[i+10 for i in [13, 0, 10, 1, 12, 1, 11, 6]])
