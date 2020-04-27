from django.apps import AppConfig
import sys


class TaxTeaConfig(AppConfig):
    """
    An AppConfig for TaxTea which loads system checks
    and event handlers once Django is ready.
    """

    name = "taxtea"
    verobose_name = "Tax Tea"

    def ready(self):
        from . import checks  # noqa: Register the checks

        if "runserver" not in sys.argv:
            return True
        from taxtea import settings
        from taxtea.models import ZipCode, State

        # Insure Origins are in the DB
        for state, zc in settings.ORIGINS:
            s = State.objects.get(pk=state)
            ZipCode.objects.get_or_create(code=zc, defaults={"code": zc, "state": s})
