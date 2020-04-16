from django.conf import settings

############
# USPS API #
############
USPS_USER = getattr(settings, "TAX_USPS_USER")
USPS_PASSWORD = getattr(settings, "TAX_USPS_PASSWORD")


###############
# Avalara Api #
###############
AVALARA_USER = getattr(settings, "TAX_AVALARA_USER")
AVALARA_PASSWORD = getattr(settings, "TAX_AVALARA_PASSWORD")
