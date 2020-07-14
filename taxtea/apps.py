from django.apps import AppConfig


class TaxTeaConfig(AppConfig):
    """
    An AppConfig for Django TaxTea which loads system checks
    and event handlers once Django is ready.
    """

    name = "django-taxtea"
    verobose_name = "Django TaxTea"

    def ready(self):
        from . import checks  # noqa: Register the checks
