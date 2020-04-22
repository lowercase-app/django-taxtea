from django.conf import settings

############
# USPS API #
############
USPS_USER = getattr(settings, "TAX_USPS_USER", None)
# USPS_PASSWORD = getattr(settings, "TAX_USPS_PASSWORD")


###############
# Avalara Api #
###############
