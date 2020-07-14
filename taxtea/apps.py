import sys

from django.apps import AppConfig


class TaxTeaConfig(AppConfig):
    """
    An AppConfig for TaxTea which loads system checks
    and event handlers once Django is ready.
    """

    name = "taxtea"
    verobose_name = "Tax Tea"

    def ready(self):
        from . import checks  # noqa: Register the checks
