"""
Tax Exceptions
"""


class USPSError(Exception):
    pass


class AvalaraError(Exception):
    pass


class AvalaraRateLimit(AvalaraError):
    pass
