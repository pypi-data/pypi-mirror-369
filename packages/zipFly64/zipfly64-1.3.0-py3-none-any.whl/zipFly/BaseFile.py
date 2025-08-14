import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Generator

from . import consts
from .Compressor import Compressor


class BaseFile(ABC):
    def __init__(self, name: str, compression_method: int = consts.NO_COMPRESSION):
        self.__used = False
        self.__compressed_size = 0
        self.__offset = 0  # Offset to local file header
        self.__crc = 0
        self.__compression_method = compression_method
        self.__flags = 0b00001000  # flag about using data descriptor is always on
        self.__byte_offset_mode = False
        if name == "":
            raise KeyError("File name cannot be blank.")
        self._name = name

    def __str__(self):
        return f"BaseFile[name={self._name}]"

    def __repr__(self):
        return f"BaseFile({self._name})"

    def _check_if_used(self):
        if self.__used:
            raise RuntimeError("Do not re-use file instances. Recreate it.")
        self.__used = True

    def generate_processed_file_data(self) -> Generator[bytes, None, None]:
        """Generates compressed file data"""
        self._check_if_used()
        compressor = Compressor(self)

        for chunk in self._generate_file_data():
            chunk = compressor.process(chunk)
            if len(chunk) > 0:
                yield chunk
        chunk = compressor.tail()
        if len(chunk) > 0:
            yield chunk

    async def async_generate_processed_file_data(self) -> AsyncGenerator[bytes, None]:
        """Generates compressed file data"""
        self._check_if_used()
        compressor = Compressor(self)

        async for chunk in self._async_generate_file_data():
            chunk = compressor.process(chunk)
            if len(chunk) > 0:
                yield chunk
        chunk = compressor.tail()
        if len(chunk) > 0:
            yield chunk

    def get_mod_time(self) -> int:
        # Extract hours, minutes, and seconds from the modification time
        t = time.localtime(self.modification_time)
        return ((t.tm_hour << 11) | (t.tm_min << 5) | (t.tm_sec // 2)) & 0xFFFF

    def get_mod_date(self) -> int:
        # Extract year, month, and day from the modification time
        t = time.localtime(self.modification_time)
        year = t.tm_year - 1980  # ZIP format years start from 1980
        return ((year << 9) | (t.tm_mon << 5) | t.tm_mday) & 0xFFFF

    def set_offset(self, new_offset) -> None:
        self.__offset = new_offset

    def get_offset(self) -> int:
        return self.__offset

    def get_compressed_size(self) -> int:
        return self.__compressed_size

    def add_compressed_size(self, value) -> None:
        self.__compressed_size += value

    def set_compressed_size(self, new_value) -> None:
        self.__compressed_size = new_value

    def get_crc(self) -> int:
        return self.__crc

    def set_crc(self, new_crc) -> None:
        self.__crc = new_crc

    def set_byte_offset_mode(self, value) -> None:
        self.__byte_offset_mode = value

    def is_byte_offset_mode(self) -> bool:
        return self.__byte_offset_mode

    def set_file_name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def file_path_bytes(self) -> bytes:
        try:
            return self.name.encode("ascii")
        except UnicodeError:
            self.__flags |= consts.UTF8_FLAG
            return self.name.encode("utf-8")

    @abstractmethod
    def _generate_file_data(self) -> Generator[bytes, None, None]:
        raise NotImplementedError

    @abstractmethod
    async def _async_generate_file_data(self) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError

    @abstractmethod
    def get_predicted_crc(self) -> int:
        raise NotImplementedError

    @property
    def size(self) -> int:
        raise NotImplementedError

    @property
    def modification_time(self) -> float:
        raise NotImplementedError

    @property
    def flags(self) -> int:
        return self.__flags

    @property
    def name(self) -> str:
        return self._name

    @property
    def compression_method(self) -> int:
        return self.__compression_method
