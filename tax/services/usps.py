import xmltodict
from typing import List
from tax import settings
from tax.exceptions import USPSError

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
        if "Error" in response.text:
            raise USPSError(response.text)
        parsed = (
            xmltodict.parse(response.text).get("CityStateLookupResponse").get("ZipCode")
        )
        return parsed
