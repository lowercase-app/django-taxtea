from django.dispatch import Signal

tax_rate_changed = Signal(providing_args=["zipcode", "tax_rate"])
