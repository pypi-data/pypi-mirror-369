class HookerError(Exception):
    pass

class ProcessNotFound(HookerError):
    pass

class MemoryReadError(HookerError):
    pass

class MemoryWriteError(HookerError):
    pass
