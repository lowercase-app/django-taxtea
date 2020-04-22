import django.dispatch

tax_rate_changed = django.dispatch.Signal(provided_args=["zipcode", "tax_rate"])
