class Response:
    def __init__(self, data: bytes):
        self.data = data           # e.g  b'\x02QA1@0\x03P'
        self.stx = data[0:1]       # e.g  b'\x02'
        self.channel = data[1:2]   # e.g  b'Q'
        self.device = data[2:4]    # e.g  b'A1'
        self.status = data[4:5]    # e.g  b'@'
        self.content = data[5:-2]  # e.g  b'0'
        self.content_str = self.content.decode('utf-8')
        self.etx = data[-2:-1]     # e.g  b'\x03'
        self.xor = data[-1:]       # e.g  b'P'

    def __str__(self):
        return f'Response(stx={self.stx}, channel={self.channel}, device={self.device}, status={self.status}, content={self.content}, etx={self.etx}, xor={self.xor})'
