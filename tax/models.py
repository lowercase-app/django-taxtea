from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from localflavor.us.models import USStateField
from tax.signals import tax_rate_changed
from tax import settings


class State(models.Model):

    TAX_BASES = [("ORIGIN", "Origin-based"), ("DESTINATION", "Destination-based")]

    abbreviation = USStateField(blank=False, null=False, primary_key=True)
    collects_saas_tax = models.BooleanField(default=False)
    tax_base = models.CharField(max_length=30, choices=TAX_BASES, default="DESTINATION")

    @classmethod
    def origin_states(cls):
        return cls.objects.filter(zipcodes__in=settings.ORIGIN_ZIPCODES)

    def __str__(self):
        return f"State: {self.abbreviation}"


class ZipCode(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="zipcodes")
    code = models.CharField(max_length=9, primary_key=True)
    tax_rate = models.DecimalField(
        blank=True, max_digits=5, decimal_places=4, null=True
    )
    last_checked = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"ZipCode: {self.code}, {self.state}"


@receiver(post_save, sender=ZipCode)
def broadcast_tax_rate_change(sender, instance, update_fields, **kwargs):
    if update_fields and "tax_rate" in update_fields:
        tax_rate_changed.send(
            sender=tax_rate_changed, zipcode=instance.code, tax_rate=instance.tax_rate
        )
