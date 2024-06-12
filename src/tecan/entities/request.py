class Request:
    def __init__(self, data: bytes):
        self.data = data           # e.g  b'\x02AA1RSD1\x03D'
        self.stx = data[0:1]       # e.g  b'\x02'
        self.channel = data[1:2]   # e.g  b'A'
        self.device = data[2:4]    # e.g  b'A1'
        self.command = data[4:-2]  # e.g  b'RSD1'
        self.etx = data[-2:-1]     # e.g  b'\x03'
        self.xor = data[-1:]       # e.g  b'D'

    def __str__(self):
        return f'Request(stx={self.stx}, channel={self.channel}, device={self.device}, command={self.command}, etx={self.etx}, xor={self.xor})'
