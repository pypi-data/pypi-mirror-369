# Base66U

Base66U is a new binary-to-text encoding that is:
- URL-safe (RFC 3986 unreserved characters only)
- Padding-free
- Slightly denser than Base64
- Optional CRC-16 checksum support

## Install

```bash
pip install base66u
```

## Usage

```python
from base66u import b66u_encode, b66u_decode

data = b"Hello"
encoded = b66u_encode(data)
decoded = b66u_decode(encoded)
assert decoded == data
```
