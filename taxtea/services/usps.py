from typing import List

import httpx
import xmltodict

from taxtea import settings
from taxtea.exceptions import USPSError


class USPSService:
    """
    USPSService:
        Base service for interacting with the USPS API.

    Note:
        Class has no functionality on its own. Just holds service url and auth.

    Attributes:
        BASE_URL (str): USPS API base url
        USER (str): USPS API User
    """

    BASE_URL = "https://secure.shippingapis.com/ShippingAPI.dll"
    USER = settings.USPS_USER


class ZipService(USPSService):
    """
    ZipService:
        Service to find the cities and states for a given zipcode(s).

    Attributes:
        BASE_URL (str): USPS API base url
    """

    BASE_URL = f"{USPSService.BASE_URL}?API=CityStateLookup"

    def _generate_xml_payload(zipcodes: List[str]) -> str:
        """
        _generate_xml_payload:
            Generates the xml payload that will be sent to the USPS API.

        Args:
            zipcodes (List[str]): Zip Codes to get City/State for

        Note: Max 5 Zip Codes at a time

        Raises:
            TypeError: Raises TypeError if invalid Zip Code

        Returns:
            str: An XML payload
        """
        for z in zipcodes:
            if len(z) != 5:
                raise TypeError("Invalid Zip Code")

        payload = {
            "CityStateLookupRequest": {
                "@USERID": USPSService.USER,
                "ZipCode": [{"Zip5": zip} for zip in zipcodes],
            }
        }
        return xmltodict.unparse(payload)

    @classmethod
    def lookup_zip(cls, zipcode: str) -> dict:
        """
        lookup_zip:
            Retrieves a city/state pairing for a given zip code via USPS API.

        Args:
            zipcode (str): ZipCode to query.

        Raises:
            USPSError: Usually an invalid zip code, but could be any USPS Service Error.

        Returns:
            dict: {"Zip5":20024, "City":"WASHINGTON", "State":"DC"}
        """
        url = f"{cls.BASE_URL}&XML={cls._generate_xml_payload([zipcode])}"
        response = httpx.get(url)
        if "Error" in response.text:
            raise USPSError(response.text)
        parsed = (
            xmltodict.parse(response.text).get("CityStateLookupResponse").get("ZipCode")
        )
        return parsed
