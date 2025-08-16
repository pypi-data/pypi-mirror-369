from .alphabet import ALPHABET, INDEX, BASE

def crc16_ccitt_false(data: bytes) -> int:
    """CRC-16/CCITT-FALSE checksum."""
    crc = 0xFFFF
    poly = 0x1021
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) & 0xFFFF) ^ poly
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def encode_checksum(crc: int) -> str:
    """Encode a 16-bit checksum into exactly 3 Base66U digits."""
    c0 = crc % BASE
    c1 = (crc // BASE) % BASE
    c2 = (crc // (BASE * BASE)) % BASE
    return ALPHABET[c2] + ALPHABET[c1] + ALPHABET[c0]

def decode_checksum(chk: str) -> int:
    """Decode a 3-character checksum back to integer."""
    if len(chk) != 3:
        raise ValueError("Checksum must be 3 characters")
    c2 = INDEX[chk[0]]
    c1 = INDEX[chk[1]]
    c0 = INDEX[chk[2]]
    return c0 + c1 * BASE + c2 * BASE * BASE
