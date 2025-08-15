def bytes_to_hex(data: bytes):
    return ' '.join(f'{b:02X}' for b in data)
