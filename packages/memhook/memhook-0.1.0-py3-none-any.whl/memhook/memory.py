import ctypes
from .process import kernel32
from .exceptions import MemoryReadError, MemoryWriteError

class Memory:
    def __init__(self, handle):
        self.handle = handle

    def read(self, address, size):
        buffer = ctypes.create_string_buffer(size)
        bytesRead = ctypes.c_size_t()
        if not kernel32.ReadProcessMemory(self.handle, address, buffer, size, ctypes.byref(bytesRead)):
            raise MemoryReadError(f"Failed to read memory at {hex(address)}")
        return buffer.raw

    def write(self, address, data: bytes):
        size = len(data)
        c_data = ctypes.create_string_buffer(data)
        bytesWritten = ctypes.c_size_t()
        if not kernel32.WriteProcessMemory(self.handle, address, c_data, size, ctypes.byref(bytesWritten)):
            raise MemoryWriteError(f"Failed to write memory at {hex(address)}")
        return True

    def read_int(self, address):
        return int.from_bytes(self.read(address, 4), byteorder='little')

    def write_int(self, address, value):
        self.write(address, value.to_bytes(4, byteorder='little'))

    def read_float(self, address):
        import struct
        return struct.unpack('f', self.read(address, 4))[0]

    def write_float(self, address, value):
        import struct
        self.write(address, struct.pack('f', value))
