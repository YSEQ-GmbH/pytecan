import serial
from tecan.entities import Command
from tecan.firmware.standard import Standard


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
    # respone = firmware.send_command(
    #     Command('A1', 'PAY', params=[-800, 90 + 6]))
    # print(respone.content_str)

    while True:
        firmware.read()


if __name__ == '__main__':
    main()
