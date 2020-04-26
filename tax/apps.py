from django.apps import AppConfig
import sys


class TaxConfig(AppConfig):
    """
    An AppConfig for Tax which loads system checks
    and event handlers once Django is ready.
    """

    name = "tax"
    verobose_name = "Tax"

    def ready(self):
        from . import checks  # noqa: Register the checks

        if "runserver" not in sys.argv:
            return True
        from tax import settings
        from tax.models import ZipCode, State

        # Insure Origins are in the DB
        for state, zc in settings.ORIGINS:
            s = State.objects.get(pk=state)
            ZipCode.objects.get_or_create(code=zc, defaults={"code": zc, "state": s})
