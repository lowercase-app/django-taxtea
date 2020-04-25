# Core API of Tax Django App

from tax.models import State, ZipCode
from tax.services.usps import ZipService




def stateForZip(zipCode: str) -> State:
    res = ZipService.lookup_zips([zipCode])
    return State.objects.get(abbreviation=res.get("State"))
