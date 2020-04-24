from django.apps import AppConfig


class TaxConfig(AppConfig):
    """
    An AppConfig for Tax which loads system checks
    and event handlers once Django is ready.
    """

    name = "tax"
    verobose_name = "Tax"

    def ready(self):
        from . import checks  # noqa: Register the checks
