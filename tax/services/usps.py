import xmltodict

# from django.conf import settings
import httpx


class USPSService:
    """
    Base service for interacting with the USPS API.
    """

    BASE_URL = "https://secure.shippingapis.com/ShippingAPI.dll?"
    USER = "***REMOVED***"


class ZipService(USPSService):
    """
    Service to find the cities and states for a given zipcode(s).
    """

    BASE_URL = f"{USPSService.BASE_URL}API=CityStateLookup"

    @classmethod
    def _generate_xml_payload(cls, zipcodes: list):
        payload = {
            "CityStateLookupRequest": {
                "@USERID": USPSService.USER,
                "ZipCode": [{"Zip5": zip} for zip in zipcodes],
            }
        }
        return xmltodict.unparse(payload)

    @classmethod
    def lookup_zips(cls, zipcodes: list):
        url = f"{ZipService._BASE_URL}&XML={cls._generate_xml_payload(zipcodes)}"
        response = httpx.get(url)
        return xmltodict.parse(response.text)


if __name__ == "__main__":
    print(ZipService.lookup_zips(["12345", "27587", "44136", "44149", "44120"]))
