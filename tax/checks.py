from django.core import checks


@checks.register("Tax")
def check_USPS_api_auth(appconfig=None, **kwargs):
    """Checks if the user has supplied a USPS username/password."""
    from . import settings as tax_settings

    messages = []

    if not tax_settings.USPS_USER:
        msg = "Could not find a USPS User."
        hint = "Add TAX_USPS_USER to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C001"))

    return messages


@checks.register("Tax")
def check_Avalara_api_auth(appconfig=None, **kwargs):
    """Checks if the user has supplied a Avalara username/password."""
    from . import settings as tax_settings

    messages = []

    if not tax_settings.AVALARA_USER:
        msg = "Could not find a Avalara User."
        hint = "Add TAX_AVALARA_USER to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C002"))
    if not tax_settings.AVALARA_PASSWORD:
        msg = "Could not find a Avalara Password."
        hint = "Add TAX_AVALARA_PASSWORD to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C003"))

    return messages


@checks.register("Tax")
def check_origin_zips(appconfig=None, **kwargs):
    """Checks if the user has supplied at least one origin zip"""
    from . import settings as tax_settings

    messages = []

    if not tax_settings.TAX_ORIGIN_ZIPCODES:
        msg = "Could not find a Origin Zipcode."
        hint = "Add at least one TAX_ORIGIN_ZIPCODES to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C004"))

    return messages
