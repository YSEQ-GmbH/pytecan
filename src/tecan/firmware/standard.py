from serial import Serial
from .firmware import Firmware
from ..entities import Request, Response


__all__ = ['Standard']
CHANNELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ERRORS = table = {
    1: "Initialization failed",
    2: "Invalid command",
    3: "Invalid operand",
    4: "CAN acknowledge problems",
    5: "Device not implemented",
    6: "CAN answer timeout",
    7: "Device not initialized",
    8: "Command overflow of TeCU",
    9: "No liquid detected",
    10: "Drive no load",
    11: "Not enough liquid",
    12: "Not enough liquid",
    13: "No Flash access",
    15: "Command overflow of subdevice",
    17: "Measurement failed",
    18: "Clot limit passed",
    19: "No clot exit detected",
    20: "No liquid exit detected",
    21: "Delta pressure overrun (pLLD)",
    22: "Tip Guard in wrong position",
    23: "Not yet moved or move aborted",
    24: "llid pulse error or reed crosstalk error",
    25: "Tip not fetched",
    26: "Tip not mounted",
    27: "Tip mounted",
    28: "Subdevice error",
    29: "Application switch and axes mismatch",
    30: "Wrong DC-Servo type",
    31: "Virtual Drive"
}


def calculate_xor(data_bytes) -> int:
    checksum = 0
    for byte in data_bytes:
        checksum ^= byte
    return checksum


class Standard(Firmware):
    def __init__(self, serial):
        self.serial: Serial = serial
        self.channel_position = 16

    def send_command(self, command):
        global CHANNELS

        request: Request = self.build_request(command)
        self.write(request.data)

        acknowledge = self.read()

        response = Response(self.read())
        response_channel = bytes(
            [ord(response.channel) - self.channel_position])

        if response_channel == request.channel:
            CHANNELS.append(response_channel.decode('utf-8'))
            CHANNELS = sorted(CHANNELS)
            self.write(acknowledge)
        else:
            self.write(acknowledge)
            self.close()
            error_code = self.decode_error(response.status)
            if error_code in ERRORS:
                raise Exception(f'Error: {ERRORS[error_code]}')
            raise Exception(f'Invalid response channel {response.data}')

        return response

    def read(self, size=None):
        try:
            if size is None:
                while self.serial.read(1) != b'\x02':
                    pass
                data = b'\x02' + \
                    self.serial.read_until(b'\x03') + self.serial.read(1)
            else:
                data = self.serial.read(size)
        except KeyboardInterrupt:
            self.close()
            exit(0)

        print(f'- {data}')

        return data

    def write(self, data):
        print(f'> {data}')
        # Check if the data is valid before sending it to the robot
        if not data.startswith(b'\x02'):
            raise ValueError('Data must start with STX')
        if data[-2:-1] != b'\x03':
            raise ValueError('Data must end with ETX')
        if not data.endswith(bytes([calculate_xor(data[:-1])])):
            raise ValueError('Invalid LRC')

        self.serial.flushInput()
        self.serial.write(data)

    def build_request(self, command):
        global CHANNELS

        stx = b'\x02'
        etx = b'\x03'
        channel = CHANNELS.pop(0)
        full_message = stx + bytes(channel, 'utf-8') + \
            command.full_command + etx
        lrc = calculate_xor(full_message)
        full_message += bytes([lrc])
        return Request(full_message)

    def close(self):
        self.serial.close()

    def decode_error(self, error_chr) -> int:
        ascii_value = ord(error_chr)
        decoded_value = ascii_value - 0x40
        return decoded_value
