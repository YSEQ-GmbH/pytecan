import serial
from tecan.entities import Command
from tecan.firmware.standard import Standard, calculate_xor


def init():
    usb_serial = serial.Serial(
        port='/dev/tty.usbserial-110',
        baudrate=9600,
        timeout=60*5,
        writeTimeout=5,
        interCharTimeout=10
    )

    return Standard(usb_serial)


def main():
    firmware = init()
    data = b'\x02\x1f1YIP100OS9OD100R\x03'
    checksum = calculate_xor(data)
    firmware.write(data + bytes([checksum]))

    while True:
        print(firmware.read())


if __name__ == '__main__':
    main()
