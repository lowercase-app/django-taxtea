# Core API of Tax Django App

from tax.models import State, ZipCode
from tax.services.usps import ZipService


def connectZipToState(zipCode: str):
    # Create Zipcode & link to state in DB from USPS
    res = ZipService.lookup_zips([zipCode])
    citystate = res.pop()
    state = State.objects.get(abbreviation=citystate.get("State"))
    return ZipCode.objects.create(code=citystate.get("Zip5"), state=state)


def stateForZip(zipCode: str) -> State:
    res = ZipService.lookup_zips([zipCode])
    return State.objects.get(abbreviation=res.get("State"))
