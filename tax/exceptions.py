"""
Tax Exceptions
"""


class USPSError(Exception):
    pass


class AlavaraError(Exception):
    pass


class AvalaraRateLimit(AlavaraError):
    pass
