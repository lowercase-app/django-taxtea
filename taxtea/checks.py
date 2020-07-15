from typing import List

from django.apps.config import AppConfig
from django.core import checks


@checks.register("TaxTea")
def check_USPS_api_auth(app_configs: AppConfig = None) -> List[checks.CheckMessage]:
    """
    check_USPS_api_auth:
        Checks if the user has supplied a USPS username/password.

    Args:
        appconfig (AppConfig, optional): Defaults to None.

    Returns:
        List[checks.CheckMessage]: List of Django CheckMessages
    """
    from . import settings as tax_settings

    messages = []

    if not tax_settings.USPS_USER:
        msg = "Could not find a USPS User."
        hint = "Add TAXTEA_USPS_USER to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C001"))

    return messages


@checks.register("TaxTea")
def check_Avalara_api_auth(app_configs: AppConfig = None) -> List[checks.CheckMessage]:
    """
    check_Avalara_api_auth:
        Checks if the user has supplied a Avalara username/password.

    Args:
        appconfig (AppConfig, optional): Defaults to None.

    Returns:
        List[checks.CheckMessage]: List of Django CheckMessages
    """
    from . import settings as tax_settings

    messages = []

    if not tax_settings.AVALARA_USER:
        msg = "Could not find a Avalara User."
        hint = "Add TAXTEA_AVALARA_USER to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C002"))
    if not tax_settings.AVALARA_PASSWORD:
        msg = "Could not find a Avalara Password."
        hint = "Add TAXTEA_AVALARA_PASSWORD to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C003"))

    return messages


@checks.register("TaxTea")
def check_origin_zips(app_configs: AppConfig = None) -> List[checks.CheckMessage]:
    """
    check_origin_zips:
        Checks if the user has supplied at least one origin zip.

    Args:
        appconfig (AppConfig, optional): Defaults to None.

    Returns:
        List[checks.CheckMessage]: List of Django CheckMessages
    """
    from . import settings as tax_settings

    messages = []

    if not tax_settings.NEXUSES:
        msg = "Could not find a Nexus."
        hint = "Add at least one TAXTEA_NEXUSES to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C004"))
        # If there is no TAX_NEXUS, then the next check will throw an IndexError
        return messages

    state, zipcode = tax_settings.NEXUSES[0]
    if not state and not zipcode:
        msg = "Could not find a valid Nexus tuple."
        hint = "Add at least one Nexus tuple ('STATE', 'ZIPCODE') to your settings."
        messages.append(checks.Critical(msg, hint=hint, id="tax.C005"))

    return messages
