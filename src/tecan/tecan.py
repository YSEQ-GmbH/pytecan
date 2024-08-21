import time
import serial
from .firmware import Firmware
from .entities import Command


class Tecan:
    def __init__(self, port: str,  firmware: int):
        self.__firmware = firmware
        self.__port = port
        self.__is_liha_connected = False
        self.__is_pos_id_connected = False
        self.__is_roma_connected = False

    @property
    def is_liha_connected(self):
        return self.__is_liha_connected

    @property
    def is_pos_id_connected(self):
        return self.__is_pos_id_connected

    @property
    def is_roma_connected(self):
        return self.__is_roma_connected

    def setup(self):
        self.serial = serial.Serial(
            port=self.__port,
            baudrate=9600,
            timeout=60*5,
            writeTimeout=5,
            interCharTimeout=10
        )

        # clean the buffer before starting the communication to avoid any garbage data
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        if self.__firmware == Firmware.STANDARD:
            from .firmware.standard import Standard
            self.firmware = Standard(self.serial)
        elif self.__firmware == Firmware.FREEDOM:
            raise Exception('Freedom firmware is not supported yet')
        else:
            raise Exception('Invalid firmware')

        response = self.firmware.send_command(Command('M1', 'RHW'))
        if self.__firmware == Firmware.STANDARD and not response.content_str in ['0', '1']:
            self.firmware.close()
            raise Exception('Invalid firmware')

        response = self.firmware.send_command(Command('M1', 'RFV', params=[0]))
        if not response.content_str.startswith('GENESIS'):
            self.firmware.close()
            raise Exception(f'No support for {response.content_str} !')

        self.firmware.send_command(Command('M1', 'PIS'))

        response = self.firmware.send_command(Command('M1', 'REE'))
        liha_status, pos_id_status, roma_status = list(response.content_str)

        if self.firmware.decode_error(liha_status) == 0:
            self.__is_liha_connected = True

        if self.firmware.decode_error(pos_id_status) == 0:
            self.__is_pos_id_connected = True

        if self.firmware.decode_error(roma_status) == 0:
            self.__is_roma_connected = True

    def close(self):
        time.sleep(2)
        self.firmware.close()
        self.serial.close()
