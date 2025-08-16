from .alphabet import ALPHABET, INDEX, BASE
from .checksum import crc16_ccitt_false, encode_checksum, decode_checksum
from .exceptions import (
    Base66UError,
    InvalidCharacterError,
    ChecksumMismatchError,
    MissingChecksumError,
    DanglingSeparatorError
)

def b66u_encode(data: bytes, with_checksum: bool = False) -> str:
    """Encode bytes to Base66U string."""
    if not data:
        return ""
    
    # Count leading zeros
    z = 0
    for b in data:
        if b == 0:
            z += 1
        else:
            break
    payload = data[z:]
    
    # Big integer conversion
    if payload:
        n = int.from_bytes(payload, "big")
        digits = []
        while n > 0:
            n, rem = divmod(n, BASE)
            digits.append(ALPHABET[rem])
        digits = "".join(reversed(digits))
    else:
        digits = ""
    
    out = "0" * z + digits
    
    if with_checksum:
        crc = crc16_ccitt_false(data)
        chk = encode_checksum(crc)
        if out.endswith("~"):
            out += "~"  # escape rule
        out += "~" + chk
    return out


def b66u_decode(s: str, with_checksum: bool = False) -> bytes:
    """Decode Base66U string to bytes."""
    if not s:
        return b""
    
    chk = None
    core = s
    
    if with_checksum:
        if len(s) < 4:
            raise MissingChecksumError()
        sep = s.rfind("~")
        if sep == -1 or len(s) - sep != 4:
            raise MissingChecksumError()
        chk = s[sep+1:]
        core = s[:sep]
        if core.endswith("~~"):
            core = core[:-1]  # unescape
        elif core.endswith("~"):
            raise DanglingSeparatorError()
    
    # Count leading '0'
    z = 0
    for ch in core:
        if ch == "0":
            z += 1
        else:
            break
    
    payload = core[z:]
    n = 0
    for ch in payload:
        try:
            d = INDEX[ch]
        except KeyError:
            raise InvalidCharacterError(ch)
        n = n * BASE + d
    
    if n == 0 and payload:
        body = b"\x00"
    else:
        body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    
    out = b"\x00" * z + body
    
    if with_checksum:
        crc = crc16_ccitt_false(out)
        expected = decode_checksum(chk)
        if crc != expected:
            raise ChecksumMismatchError(expected, crc)
    
    return out
