from django.dispatch import Signal

tax_rate_changed = Signal(provided_args=["zipcode", "tax_rate"])
