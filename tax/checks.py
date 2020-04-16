from django.core import checks
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


@checks.register("tax")
def check_USPS_api_auth(appconfig=None, **kwargs):
    """Checks if the user has supplied a USPS username/password."""
    from . import settings as tax_settings

    messages = []

    if not tax_settings.USPS_USER:
        msg = "Could not find a USPS User."
        hint = "Add USPS_USER to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C001"))
    if not tax_settings.USPS_PASSWORD:
        msg = "Could not find a USPS Password."
        hint = "Add USPS_PASSWORD to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C001"))

    return messages
