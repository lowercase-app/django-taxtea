from decimal import Decimal

import httpx

from taxtea import settings
from taxtea.exceptions import AvalaraError, AvalaraRateLimit


class AvalaraService:
    """
    AvalaraService:
        Shell service that has no functionality. Holds authentication and url for Avalara.

    Note:
        Not to be used on its own.
    """

    BASE_URL = "https://rest.avatax.com/api/v2/taxrates"
    USER = settings.AVALARA_USER
    PASSWORD = settings.AVALARA_PASSWORD


class TaxRate(AvalaraService):
    """
    TaxRate:
        Interface for the fetching Tax Rates from Avalara

    Args:
        AvalaraService (AvalaraService): Inherits from AvalaraService
    """

    def by_zip_code(zipcode: str, country: str = "US") -> Decimal:
        """
        by_zip_code:
            Get Tax Rate for Zip Code from Avalara

        Args:
            zipcode (str): 5 Digit Zip Code
            country (str, optional): Country code. Defaults to "US".

        Raises:
            AvalaraRateLimit: Avalara Limit Reached, retry request later
            AvalaraError: Generic Avalara Error

        Returns:
            taxrate (Decimal): Decimal value of Tax Rate, example - 0.0625
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
