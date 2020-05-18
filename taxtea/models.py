from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta

from decimal import Decimal
from typing import List, TypeVar

from localflavor.us.models import USStateField
from taxtea import settings
from taxtea.services.avalara import TaxRate
from taxtea.services.usps import ZipService
from taxtea.exceptions import InvalidZipCode

ZipCodeType = TypeVar("ZipCodeType", bound="ZipCode")


class State(models.Model):

    TAX_BASES = [("ORIGIN", "Origin-based"), ("DESTINATION", "Destination-based")]

    abbreviation = USStateField(blank=False, null=False, primary_key=True)
    collects_saas_tax = models.BooleanField(default=False)
    tax_base = models.CharField(max_length=30, choices=TAX_BASES, default="DESTINATION")

    @classmethod
    def state_for_zip(cls, zipcode: str):
        try:
            state = cls.objects.get(zipcodes=zipcode)
            return state
        except ObjectDoesNotExist:
            # nothing in DB, search USPS for it
            res = ZipService.lookup_zip(zipcode)
            # update db
            state = cls.objects.get(abbreviation=res.get("State"))
            return state

    def __str__(self):
        return f"State: {self.abbreviation}"


class ZipCode(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="zipcodes")
    code = models.CharField(max_length=9, primary_key=True)
    tax_rate = models.DecimalField(
        blank=True, max_digits=5, decimal_places=4, null=True
    )
    last_checked = models.DateTimeField(blank=True, null=True)

    @property
    def applicable_tax_rate(self) -> Decimal:
        nexuses = ZipCode.nexuses()
        zcs = nexuses + [self]
        ZipCode.__refresh_rates(zip_codes=zcs)
        self.refresh_from_db()

        for nexus in ZipCode.nexuses():
            if self.state == nexus.state and nexus.state.tax_base == "ORIGIN":
                return nexus.tax_rate
        # Destination Based
        return self.tax_rate if self.state.collects_saas_tax else Decimal("0.00")

    @classmethod
    def tax_rate_to_percentage(tax_rate: Decimal) -> Decimal:
        percentage = tax_rate * Decimal("100.00")
        return percentage.quantize(Decimal("0.0001"))

    @classmethod
    def get(cls, zip_code: str) -> ZipCodeType:
        cls.__validate(zip_code)
        try:
            return cls.objects.select_related("state").get(pk=zip_code)
        except ObjectDoesNotExist:
            state = State.state_for_zip(zip_code)
            return cls.objects.create(code=zip_code, state=state)

    @classmethod
    def nexuses(cls):
        return [
            cls.objects.get_or_create(
                pk=zc, defaults={"code": zc, "state": State.objects.get(pk=state)}
            )[0]
            for state, zc in settings.NEXUSES
        ]

    @classmethod
    def __refresh_rates(cls, zip_codes: List[ZipCodeType], force=False):
        now = timezone.now()
        for zc in zip_codes:
            if (
                force
                or not zc.last_checked
                or not zc.tax_rate
                or zc.last_checked
                + timedelta(days=settings.TAX_RATE_INVALIDATE_INTERVAL)
                < now
            ):
                # Request updated rate from Avalara API
                zc.tax_rate = TaxRate.by_zip_code(zc.code)
                zc.last_checked = now
            zc.save()

    def __str__(self):
        return f"ZipCode: {self.code}, {self.state}"

    @classmethod
    def __validate(cls, zip_code: str):
        if type(zip_code) is not str or len(zip_code) != 5 or not zip_code.isdecimal():
            raise InvalidZipCode
