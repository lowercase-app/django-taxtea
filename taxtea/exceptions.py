"""
Tax Tea Exceptions
"""


class USPSError(Exception):
    pass


class AvalaraError(Exception):
    pass


class AvalaraRateLimit(AvalaraError):
    pass


class InvalidZipCode(Exception):
    pass
