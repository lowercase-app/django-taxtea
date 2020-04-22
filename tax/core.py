# Core API of Tax Django App
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings

from tax.models import State, ZipCode
from tax.services.usps import ZipService
from tax.services.avalara import TaxRate
from collections import OrderedDict

RES_DATA = [
    OrderedDict([("Zip5", "12345"), ("City", "SCHENECTADY"), ("State", "NY"),]),
    OrderedDict([("Zip5", "27587"), ("City", "WAKE FOREST"), ("State", "NC"),]),
    OrderedDict([("Zip5", "44136"), ("City", "STRONGSVILLE"), ("State", "OH"),]),
    OrderedDict([("Zip5", "44149"), ("City", "STRONGSVILLE"), ("State", "OH"),]),
    OrderedDict([("Zip5", "44120"), ("City", "CLEVELAND"), ("State", "OH"),]),
]


def __connectZipToState(zipCode: str):
    # Create Zipcode & link to state in DB from USPS
    res = ZipService.lookup_zips(list(zipCode))
    citystate = res.pop()
    state = State.objects.get(abbreviation=citystate.get("State"))
    return ZipCode.objects.create_zip(code=citystate.get("Zip5"), state=state)


def __stateForZip(zipCode: str) -> str:
    res = ZipService.lookup_zips(list(zipCode))
    citystate = res.pop()
    return citystate.get("State")


def getTaxRateFor(zipCode: str) -> float:
    # First try a DB lookup to see if we already have a recent version of the tax rate
    try:
        zc = ZipCode.objects.select_related("state").get(code=zipCode)
    except ObjectDoesNotExist:
        zc = ZipCode.objects.create_zip(code=zipCode, state=__stateForZip)

    now = timezone.now()
    if (
        not zc.last_checked
        or not zc.tax_rate
        or zc.last_checked + timezone.delta(days=settings.TAX_RATE_INVALIDATE_INTERVAL)
        < now
    ):
        # Request updated rate from Avalara API
        tax_rate = TaxRate.by_postal_code(zipCode)
        zc.tax_rate = tax_rate
        zc.last_checked = now
        zc.save()

    return zc.tax_rate
