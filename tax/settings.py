from django.conf import settings

############
# USPS API #
############
USPS_USER = getattr(settings, "TAX_USPS_USER", None)
# USPS_PASSWORD = getattr(settings, "TAX_USPS_PASSWORD")


###############
# Avalara Api #
###############
AVALARA_USER = getattr(settings, "TAX_AVALARA_USER", None)
AVALARA_PASSWORD = getattr(settings, "TAX_AVALARA_PASSWORD", None)

#######
# TAX #
#######

# Interval to wait before pulling a new tax rate from Avalara (in Days)
TAX_RATE_INVALIDATE_INTERVAL = getattr(settings, "TAX_INVALIDATE_INTERVAL", 7)
# ZipCodes where you have a physical presence
ORIGIN_ZIPCODES = getattr(settings, "TAX_ORIGIN_ZIPCODES")
