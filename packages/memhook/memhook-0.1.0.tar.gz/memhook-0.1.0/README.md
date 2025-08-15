# Hooker

Hooker is a modern Python library for reading and writing memory of running processes on Windows.

## Features

- Attach to a process by name or PID
- Read/write bytes, integers, floats
- Safe error handling
- Convenience utilities

## Example

```python
from hooker import Hooker, Memory

h = Hooker("notepad.exe")
mem = Memory(h.handle)

# Read 4 bytes
data = mem.read(0x12345678, 4)
print(data)

# Write integer
mem.write_int(0x12345678, 1337)
```
