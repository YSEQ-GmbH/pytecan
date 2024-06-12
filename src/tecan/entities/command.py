class Command:
    def __init__(self, device: str, command: str):
        self.command: bytes = bytes(command, 'utf-8')
        self.device: bytes = bytes(device, 'utf-8')
