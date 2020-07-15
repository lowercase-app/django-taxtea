from datetime import timedelta
from decimal import Decimal
from typing import List, TypeVar

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from localflavor.us.models import USStateField

from taxtea import settings
from taxtea.exceptions import InvalidZipCode
from taxtea.services.avalara import TaxRate
from taxtea.services.usps import ZipService

ZipCodeType = TypeVar("ZipCodeType", bound="ZipCode")


class State(models.Model):
    """
    State:
        Django Model for State

    Attributes:
        abbreviation (USStateField): State Abbreviaion -> NY
        collects_saas_tax (BooleanField): Whether a state collects SaaS tax
        tax_base (CharField): Whether a state is ORIGIN or DESTINATION based
    """

    TAX_BASES = [("ORIGIN", "Origin-based"), ("DESTINATION", "Destination-based")]

    abbreviation = USStateField(blank=False, null=False, primary_key=True)
    collects_saas_tax = models.BooleanField(default=False)
    tax_base = models.CharField(max_length=30, choices=TAX_BASES, default="DESTINATION")

    @classmethod
    def state_for_zip(cls, zipcode: str):
        """
        state_for_zip [summary]

        Args:
            zipcode (str): [description]

        Returns:
            [type]: [description]
        """
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
    """
    ZipCode:
        Django Model for ZipCode

    Attributes:
        state (ForeignKey): Foreign Key to the State the ZipCode is in
        code (CharField): The 5 digit Zip Code
        tax_rate (DecimalField): Tax Rate for the given ZipCode -> 0.0625
        last_checked (DateTimeField): DateTime of the last time the tax rate was refreshed
    """

    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="zipcodes")
    code = models.CharField(max_length=9, primary_key=True)
    tax_rate = models.DecimalField(
        blank=True, max_digits=5, decimal_places=4, null=True
    )
    last_checked = models.DateTimeField(blank=True, null=True)

    @property
    def applicable_tax_rate(self) -> Decimal:
        """
        applicable_tax_rate:
            Calculates the applicable tax rate for a given ZipCode.
            Always use this over the the ZipCode's `tax_rate` field, becuase
            it takes into account tax nexues & Origin/Destination States to provide
            a true tax rate to charge.

        Returns:
            Decimal: Tax Rate to charge for ZipCode (0.0625)
        """
        nexuses = ZipCode.nexuses()
        zcs = nexuses + [self]
        ZipCode._refresh_rates(zip_codes=zcs)
        self.refresh_from_db()

        for nexus in ZipCode.nexuses():
            if self.state == nexus.state and nexus.state.tax_base == "ORIGIN":
                return nexus.tax_rate
        # Destination Based
        return self.tax_rate if self.state.collects_saas_tax else Decimal("0.00")

    @classmethod
    def tax_rate_to_percentage(cls, tax_rate: Decimal) -> Decimal:
        """
        tax_rate_to_percentage:
            Converts tax rate to percentage

        Args:
            tax_rate (Decimal): Tax Rate

        Returns:
            Tax Rate Percentage (Decimal): Example -> 6.2500
        """
        percentage = tax_rate * Decimal("100.00")
        return percentage.quantize(Decimal("0.0001"))

    @classmethod
    def get(cls, zip_code: str) -> ZipCodeType:
        """
        get:
            Get ZipCode Object for zip_code string.
            Always use this method to fetch ZipCodes, as it will
            get or create the ZipCode object.

        Args:
            zip_code (str): Zip Code to Query

        Returns:
            ZipCodeType: ZipCode Db Object
        """
        cls._validate(zip_code)
        try:
            return cls.objects.select_related("state").get(pk=zip_code)
        except ObjectDoesNotExist:
            state = State.state_for_zip(zip_code)
            return cls.objects.create(code=zip_code, state=state)

    @classmethod
    def nexuses(cls) -> List[ZipCodeType]:
        """
        nexuses:
            Fetch Nexus ZipCodes

        Returns:
            List[ZipCodeType]: List of Nexus ZipCodes
        """
        return [
            cls.objects.get_or_create(
                pk=zc, defaults={"code": zc, "state": State.objects.get(pk=state)}
            )[0]
            for state, zc in settings.NEXUSES
        ]

    @classmethod
    def _refresh_rates(cls, zip_codes: List[ZipCodeType], force=False) -> None:
        """
        _refresh_rates:
            Refresh Rates for a given list of ZipCodes.
            Will skip any ZipCodes that are still inside the `TAX_RATE_INVALIDATE_INTERVAL`
            unless `force=True`.

        Args:
            zip_codes (List[ZipCodeType]): ZipCode Objects
            force (bool, optional): Forces the refresh. Defaults to False.
        """
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
    def _validate(cls, zip_code: str) -> None:
        """
        _validate:
            Validates a Zip Code string

        Args:
            zip_code (str):

        Raises:
            InvalidZipCode:
        """
        if type(zip_code) is not str or len(zip_code) != 5 or not zip_code.isdecimal():
            raise InvalidZipCode
