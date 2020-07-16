from decimal import Decimal

import httpx

from taxtea import settings
from taxtea.exceptions import AvalaraError, AvalaraRateLimit


class AvalaraService:
    """
    The Abstract Service that holds authentication & base url for Avalara.

    Note:
        Not to be used on its own.

    Attributes:
        BASE_URL (str): Avalara API base url
        USER (str): Avalara API User
        PASSWORD (str): Avalara API Password
    """

    BASE_URL = "https://rest.avatax.com/api/v2/taxrates"
    USER = settings.AVALARA_USER
    PASSWORD = settings.AVALARA_PASSWORD


class TaxRate(AvalaraService):
    """
    Interface for the fetching Tax Rates from Avalara

    Args:
        AvalaraService: Inherits from AvalaraService
    """

    def by_zip_code(zipcode: str, country: str = "US") -> Decimal:
        """
        Get Tax Rate for Zip Code from Avalara

        Args:
            zipcode: 5 Digit Zip Code
            country: Country code. Defaults to "US".

        Raises:
            AvalaraRateLimit: Avalara Limit Reached, retry request later
            AvalaraError: Generic Avalara Error

        Returns:
            Decimal: Decimal value of Tax Rate, example - 0.0625
        """
        url = f"{AvalaraService.BASE_URL}/bypostalcode?country={country}&postalCode={zipcode}"

        response = httpx.get(url, auth=(AvalaraService.USER, AvalaraService.PASSWORD))
        if response.status_code == 429:
            raise AvalaraRateLimit

        try:
            response.raise_for_status()
        except httpx.exceptions.HttpError as e:
            raise AvalaraError(e)

        tax_rate = Decimal(response.json().get("totalRate"))
        return tax_rate.quantize(Decimal("0.0001"))
