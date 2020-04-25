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
# A list of tuples where you have a physical prescense (origin)
# format ("STATE_ABBR", "ZIPCODE") example: ("OH", "44136")
ORIGIN_ZIPCODES = getattr(settings, "TAX_ORIGIN_ZIPCODES", [])
