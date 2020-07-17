"""
TaxTea Exceptions
"""


class USPSError(Exception):
    """
    USPSError:
        Error with the USPS Service
    """

    pass


class AvalaraError(Exception):
    """
    AvalaraError:
        Base Error for Avalara Service
    """

    pass


class AvalaraRateLimit(AvalaraError):
    """
    AvalaraRateLimit:
        Rate Limit exceeded for Avalara Service
    """

    pass


class InvalidZipCode(Exception):
    """
    InvalidZipCode:
        Invalid Zip Code
    """

    pass
