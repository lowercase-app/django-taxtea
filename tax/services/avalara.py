import httpx
from tax import settings
from tax.exceptions import AvalaraError, AvalaraRateLimit


class AvalaraService:

    BASE_URL = "https://rest.avatax.com/api/v2/taxrates"
    USER = settings.AVALARA_USER
    PASSWORD = settings.AVALARA_PASSWORD


class TaxRate(AvalaraService):
    """
    Interface for the fetching Tax Rates from Avalara
    """

    def by_postal_code(postalCode: str, country="US"):
        url = f"{AvalaraService.BASE_URL}/bypostalcode?country={country}&postalCode={postalCode}"
        try:
            response = httpx.get(
                url, auth=(AvalaraService.USER, AvalaraService.PASSWORD)
            )
        except httpx.exceptions.httpError:
            if response.status_code == 429:
                raise AvalaraRateLimit
            else:
                raise AvalaraError
        return response.json().get("totalRate")
