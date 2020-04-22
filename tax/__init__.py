"""
Tax 
"""
# import pkg_resources
from django.apps import AppConfig

# __version__ = pkg_resources.require("tax")[0].version

default_app_config = "tax.TaxAppConfig"


class TaxAppConfig(AppConfig):
    """
    An AppConfig for Tax which loads system checks
    and event handlers once Django is ready.
    """

    name = "tax"

    def ready(self):
        from . import checks  # noqa: Register the checks
