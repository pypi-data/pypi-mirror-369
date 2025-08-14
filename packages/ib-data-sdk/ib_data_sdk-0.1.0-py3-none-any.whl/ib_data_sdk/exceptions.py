class IBDataSDKError(Exception):
    """Base exception class for IB Data SDK."""

    pass


class ConnectionError(IBDataSDKError):
    """Raised when connection to IB fails."""

    pass


class DataRequestError(IBDataSDKError):
    """Raised when data request fails."""

    pass


class TimeoutError(IBDataSDKError):
    """Raised when request times out."""

    pass


class ValidationError(IBDataSDKError):
    """Raised when input validation fails."""

    pass
