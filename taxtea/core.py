# Core API of Tax Django App

from taxtea.models import State, ZipCode
from taxtea.services.usps import ZipService
from taxtea import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from typing import List, Tuple
from taxtea.services.avalara import TaxRate
from decimal import Decimal


def state_for_zip(zipcode: str) -> State:
    try:
        state = State.objects.get(zipcodes=zipcode)
        return state
    except ObjectDoesNotExist:
        # nothing in DB, search USPS for it
        res = ZipService.lookup_zip(zipcode)
        # update db
        state = State.objects.get(abbreviation=res.get("State"))
        return state


def determine_tax_method_and_rate(zipcode: ZipCode) -> Tuple[str, Decimal]:
    nexuses = ZipCode.nexuses()
    # Origin Tax Rate takes precedence
    for nexus in nexuses:
        if zipcode.state == nexus.state and nexus.state.tax_base == "ORIGIN":
            return ("ORIGIN", nexus.tax_rate)
    return ("DESTINATION", zipcode.tax_rate)


def refresh_tax_rates(zipcodes: List[ZipCode], force: bool = False) -> List[ZipCode]:
    now = timezone.now()
    for zc in zipcodes:
        if (
            force
            or not zc.last_checked
            or not zc.tax_rate
            or zc.last_checked + timedelta(days=settings.TAX_RATE_INVALIDATE_INTERVAL)
            < now
        ):
            # Request updated rate from Avalara API
            zc.tax_rate = TaxRate.by_zip_code(zc.code)
            zc.last_checked = now
            # update_fields needed to send signal
            zc.save(update_fields=["tax_rate", "last_checked"])
    return zipcodes
