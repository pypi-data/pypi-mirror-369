class AddressFrException(Exception):
    """Base exception for AddressFrpy errors."""

class AddressNotFound(AddressFrException):
    """Exception raised when an address is not found."""