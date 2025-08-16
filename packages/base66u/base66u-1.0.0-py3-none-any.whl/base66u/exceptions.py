class Base66UError(ValueError):
    """Base class for all Base66U-related errors."""
    pass


class InvalidCharacterError(Base66UError):
    """Raised when the input string contains a character not in the Base66U alphabet."""
    def __init__(self, char: str):
        super().__init__(f"Invalid character: {repr(char)}")
        self.char = char


class ChecksumMismatchError(Base66UError):
    """Raised when the provided checksum does not match the calculated value."""
    def __init__(self, expected: int, got: int):
        super().__init__(f"Checksum mismatch: expected {expected}, got {got}")
        self.expected = expected
        self.got = got


class MissingChecksumError(Base66UError):
    """Raised when checksum is expected but not found in the input string."""
    def __init__(self):
        super().__init__("Missing or misplaced checksum")


class DanglingSeparatorError(Base66UError):
    """Raised when a trailing '~' is found without a valid checksum."""
    def __init__(self):
        super().__init__("Dangling separator '~' without checksum")
