import pytest
from base66u import (
    b66u_encode,
    b66u_decode,
    InvalidCharacterError,
    ChecksumMismatchError,
    MissingChecksumError,
    DanglingSeparatorError,
)

def test_roundtrip_no_checksum():
    print("Testing roundtrip without checksum...")
    data = b"Hello"
    encoded = b66u_encode(data)
    decoded = b66u_decode(encoded)
    assert decoded == data

def test_roundtrip_with_checksum():
    print("Testing roundtrip with checksum...")
    data = b"Hello"
    encoded = b66u_encode(data, with_checksum=True)
    decoded = b66u_decode(encoded, with_checksum=True)
    assert decoded == data

def test_leading_zeros():
    print("Testing leading zeros...")
    data = b"\x00\x00Hello"
    encoded = b66u_encode(data)
    decoded = b66u_decode(encoded)
    assert decoded == data

def test_invalid_character():
    print("Testing invalid character...")
    with pytest.raises(InvalidCharacterError):
        b66u_decode("!!!")

def test_checksum_mismatch():
    print("Testing checksum mismatch...")
    bad = b66u_encode(b"test", with_checksum=True)[:-1] + "0"
    with pytest.raises(ChecksumMismatchError):
        b66u_decode(bad, with_checksum=True)

def test_missing_checksum():
    print("Testing missing checksum...")
    # with_checksum=True but no '~' + checksum part
    encoded = b66u_encode(b"abc", with_checksum=False)  # valid without checksum
    with pytest.raises(MissingChecksumError):
        b66u_decode(encoded, with_checksum=True)

def test_dangling_separator():
    print("Testing dangling separator...")
    # valid data + trailing '~' but no checksum digits
    encoded = b66u_encode(b"abc", with_checksum=False) + "~"
    with pytest.raises(MissingChecksumError):  # <-- should expect this
        b66u_decode(encoded, with_checksum=True)

if __name__ == "__main__":
    test_roundtrip_no_checksum()
    test_roundtrip_with_checksum()
    test_leading_zeros()
    test_invalid_character()
    test_checksum_mismatch()
    test_missing_checksum()
    test_dangling_separator()
    print("All tests passed!")
