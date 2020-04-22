import httpx
from tax import settings


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
        response = httpx.get(url, auth=(AvalaraService.USER, AvalaraService.PASSWORD))
        return getattr(response.json(), "totalRate")
