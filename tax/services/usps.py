import xmltodict
from typing import List
from tax import settings

# from django.conf import settings
import httpx


class USPSService:
    """
    Base service for interacting with the USPS API.
    """

    BASE_URL = "https://secure.shippingapis.com/ShippingAPI.dll?"

    USER = settings.USPS_USER


class ZipService(USPSService):
    """
    Service to find the cities and states for a given zipcode(s).
    """

    BASE_URL = f"{USPSService.BASE_URL}API=CityStateLookup"

    @classmethod
    def _generate_xml_payload(cls, zipcodes: List[str]):
        payload = {
            "CityStateLookupRequest": {
                "@USERID": USPSService.USER,
                "ZipCode": [{"Zip5": zip} for zip in zipcodes],
            }
        }
        return xmltodict.unparse(payload)

    @classmethod
    def lookup_zips(cls, zipcodes: List[str]):
        url = f"{ZipService.BASE_URL}&XML={cls._generate_xml_payload(zipcodes)}"
        response = httpx.get(url)
        return (
            xmltodict.parse(response.text).get("CityStateLookupResponse").get("ZipCode")
        )


if __name__ == "__main__":
    print(ZipService.lookup_zips(["12345", "27587", "44136", "44149", "44120"]))
