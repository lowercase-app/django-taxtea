from django.conf import settings

############
# USPS API #
############
USPS_USER = getattr(settings, "TAXTEA_USPS_USER", None)
# USPS_PASSWORD = getattr(settings, "TAXTEA_USPS_PASSWORD")


###############
# Avalara Api #
###############
AVALARA_USER = getattr(settings, "TAXTEA_AVALARA_USER", None)
AVALARA_PASSWORD = getattr(settings, "TAXTEA_AVALARA_PASSWORD", None)

#######
# TAX #
#######

# Interval to wait before pulling a new tax rate from Avalara (in Days)
TAX_RATE_INVALIDATE_INTERVAL = getattr(
    settings, "TAXTEA_TAX_RATE_INVALIDATE_INTERVAL", 7
)
# A list of tuples where you have a physical prescense (nexus)
# format ("STATE_ABBR", "ZIPCODE") example: ("OH", "44136")
NEXUSES = getattr(settings, "TAXTEA_NEXUSES", [])
