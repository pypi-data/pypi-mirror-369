import pytest
from base66u import b66u_encode, b66u_decode, Base66UError

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
    with pytest.raises(Base66UError):
        b66u_decode("!!!")

def test_checksum_mismatch():
    print("Testing checksum mismatch...")
    bad = b66u_encode(b"test", with_checksum=True)[:-1] + "0"
    with pytest.raises(Base66UError):
        b66u_decode(bad, with_checksum=True)

print("All tests passed!")


