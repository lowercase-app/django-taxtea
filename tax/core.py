# Core API of Tax Django App

from tax.models import State, ZipCode
from tax.services.usps import ZipService
from tax import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from typing import List, Tuple
from tax.services.avalara import TaxRate


def state_for_zip(zipCode: str) -> State:
    try:
        state = State.objects.get(zipcodes=zipCode)
        return state
    except ObjectDoesNotExist:
        # nothing in DB, search USPS for it
        res = ZipService.lookup_zip(zipCode)
        # update db
        state = State.objects.get(abbreviation=res.get("State"))
        return state


def determine_tax_method_and_rate(zipCode: ZipCode) -> Tuple[str, float]:
    origins = ZipCode.origins()
    # Origin Tax Rate takes precedence
    for origin in origins:
        if zipCode.state == origin.state and origin.state.tax_base == "ORIGIN":
            return ("ORIGIN", origin.tax_rate)
    return ("DESTINATION", zipCode.tax_rate)


def refresh_tax_rates(zipCodes: List[ZipCode], force: bool = False) -> List[ZipCode]:
    now = timezone.now()
    for zc in zipCodes:
        if (
            force
            or not zc.last_checked
            or not zc.tax_rate
            or zc.last_checked + timedelta(days=settings.TAX_RATE_INVALIDATE_INTERVAL)
            < now
        ):
            # Request updated rate from Avalara API
            tax_rate = TaxRate.by_postal_code(zc.code)
            zc.tax_rate = tax_rate
            zc.last_checked = now
            # update_fields needed to send signal
            zc.save(update_fields=["tax_rate", "last_checked"])
    return zipCodes
