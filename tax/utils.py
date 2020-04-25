from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from tax.services.avalara import TaxRate
from tax.models import ZipCode
from tax.core import stateForZip
from tax import settings


def get_tax_rate_for_zipcode(
    zipCode: str, return_always: bool = False, force: bool = False
) -> float:
    # First try a DB lookup to see if we already have a recent version of the tax rate
    try:
        zc = ZipCode.objects.select_related("state").get(code=zipCode)
    except ObjectDoesNotExist:
        state = stateForZip(zipCode)
        zc = ZipCode.objects.create(code=zipCode, state=state)

    now = timezone.now()
    if (
        force
        or not zc.last_checked
        or not zc.tax_rate
        or zc.last_checked + timedelta(days=settings.TAX_RATE_INVALIDATE_INTERVAL) < now
    ):
        # Request updated rate from Avalara API
        tax_rate = TaxRate.by_postal_code(zipCode)
        zc.tax_rate = tax_rate
        zc.last_checked = now
        # update_fields needed to send signal
        zc.save(update_fields=["tax_rate", "last_checked"])

    return zc.tax_rate if zc.state.collects_saas_tax or return_always else 0.00
