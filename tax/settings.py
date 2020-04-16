from django.conf import settings

############
# USPS API #
############
USPS_USER = getattr(settings, "TAX_USPS_USER")
USPS_PASSWORD = getattr(settings, "TAX_USPS_PASSWORD")
