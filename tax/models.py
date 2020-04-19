from django.db import models
from localflavor.us.models import USStateField


class State(models.Model):
    abbreviation = USStateField(blank=False, null=False)
    collects_saas_tax = models.BooleanField(default=False)

    def __str__(self):
        return f"State: {self.abbreviation}"


class ZipCode(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    code = models.CharField(max_length=9)
    tax_rate = models.DecimalField(blank=True, max_digits=3, decimal_places=2)
    last_checked = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"ZipCode: {self.code}, {self.state}"
