from django.core.exceptions import ObjectDoesNotExist
from taxtea.models import ZipCode
from taxtea.core import state_for_zip, determine_tax_method_and_rate, refresh_tax_rates
from decimal import Decimal


def get_tax_rate_for_zip_code(
    zip_code: str, return_always: bool = False, force: bool = False
) -> Decimal:
    # First try a DB lookup to see if we already have a recent version of the tax rate
    try:
        zc = ZipCode.objects.select_related("state").get(code=zip_code)
    except ObjectDoesNotExist:
        state = state_for_zip(zip_code)
        zc = ZipCode.objects.create(code=zip_code, state=state)

    # refresh relevant Zip Code tax rates
    refresh_tax_rates(ZipCode.nexuses() + [zc])
    
    # ~Should~ just be able to as long as model instances follow db updates
    # return zc.applicable_tax_rate

    tax_method, tax_rate = determine_tax_method_and_rate(zc)

    if tax_method == "ORIGIN":
        return tax_rate
    if tax_method == "DESTINATION":
        return (
            tax_rate if zc.state.collects_saas_tax or return_always else Decimal("0.00")
        )
