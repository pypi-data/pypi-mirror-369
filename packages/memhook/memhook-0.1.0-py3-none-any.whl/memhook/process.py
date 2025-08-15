import psutil
import ctypes
from .exceptions import ProcessNotFound

PROCESS_ALL_ACCESS = 0x1F0FFF
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class Hooker:
    def __init__(self, target):
        self.pid = None
        self.handle = None
        self.attach(target)

    def attach(self, target):
        if isinstance(target, int):
            self.pid = target
        else:
            matches = [p.pid for p in psutil.process_iter() if p.name().lower() == target.lower()]
            if not matches:
                raise ProcessNotFound(f"Process '{target}' not found")
            self.pid = matches[0]

        self.handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, self.pid)
        if not self.handle:
            raise ProcessNotFound(f"Cannot open process {self.pid}")
