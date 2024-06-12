from abc import ABC, abstractmethod
from typing import Optional
from ..entities import Command, Request


class Firmware(ABC):
    STANDARD = 0
    FREEDOM = 1

    @abstractmethod
    def send_command(self, command: Command):
        pass

    @abstractmethod
    def read(self, size: Optional[int] = None) -> bytes:
        pass

    @abstractmethod
    def write(self, data: bytes) -> None:
        pass

    @abstractmethod
    def build_request(self, command: Command) -> Request:
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def decode_error(self, error_chr) -> int:
        pass
