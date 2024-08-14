class Response:
    def __init__(
        self,
        stx: bytes,
        channel: bytes,
        device: bytes,
        status: bytes,
        content: bytes,
        etx: bytes,
        xor: bytes
    ):
        self.stx = stx
        self.channel = channel
        self.device = device
        self.status = status
        self.content = content
        self.content_str = self.content.decode('utf-8')
        self.etx = etx
        self.xor = xor
        self.data = stx + channel + device + status + content + etx + xor

    @classmethod
    def from_data(cls, data: bytes):
        # data                  # e.g  b'\x02QA1@0\x03P'
        stx = data[0:1]         # e.g  b'\x02'
        channel = data[1:2]     # e.g  b'Q'
        device = data[2:4]      # e.g  b'A1'
        status = data[4:5]      # e.g  b'@'
        content = data[5:-2]    # e.g  b'0'
        etx = data[-2:-1]       # e.g  b'\x03'
        xor = data[-1:]         # e.g  b'P'
        return cls(stx, channel, device, status, content, etx, xor)

    def __str__(self):
        return f'Response(stx={self.stx}, channel={self.channel}, device={self.device}, status={self.status}, content={self.content}, etx={self.etx}, xor={self.xor})'
