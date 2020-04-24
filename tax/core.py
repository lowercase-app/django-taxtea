# Core API of Tax Django App
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from tax import settings
from datetime import timedelta
from tax.models import State, ZipCode
from tax.services.usps import ZipService
from tax.services.avalara import TaxRate


def __connectZipToState(zipCode: str):
    # Create Zipcode & link to state in DB from USPS
    res = ZipService.lookup_zips(list(zipCode))
    citystate = res.pop()
    state = State.objects.get(abbreviation=citystate.get("State"))
    return ZipCode.objects.create(code=citystate.get("Zip5"), state=state)


def __stateForZip(zipCode: str) -> str:
    res = ZipService.lookup_zips([zipCode,])
    return res.get("State")


def getTaxRateForZipCode(zipCode: str) -> float:
    # First try a DB lookup to see if we already have a recent version of the tax rate
    try:
        zc = ZipCode.objects.select_related("state").get(code=zipCode)
    except ObjectDoesNotExist:
        s = __stateForZip(zipCode)
        state = State.objects.get(abbreviation=s)
        zc = ZipCode.objects.create(code=zipCode, state=state)

    now = timezone.now()
    if (
        not zc.last_checked
        or not zc.tax_rate
        or zc.last_checked + timedelta(days=settings.TAX_RATE_INVALIDATE_INTERVAL) < now
    ):
        # Request updated rate from Avalara API
        tax_rate = TaxRate.by_postal_code(zipCode)
        zc.tax_rate = tax_rate
        zc.last_checked = now
        # update_fields needed to send signal
        zc.save(update_fields=["tax_rate", "last_checked"])

    return zc.tax_rate
