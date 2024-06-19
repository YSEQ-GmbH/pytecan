from typing import Union
class Command:
    def __init__(self, device: str, command: str, params: list[Union[str, int, None]] = []):
        self.command: bytes = bytes(command, 'utf-8')
        self.device: bytes = bytes(device, 'utf-8')
        self.params: list[Union[str, int, None]] = params

    @property
    def full_command(self) -> bytes:
        params: list[bytes] = []
        for param in self.params:
            if param is None:
                params.append(b'')
            else:
                params.append(bytes(str(param), 'utf-8'))
        return self.device + self.command + b','.join(params) 
