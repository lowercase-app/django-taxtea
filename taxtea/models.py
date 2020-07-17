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
StateType = TypeVar("StateType", bound="State")


class State(models.Model):
    """Django Model for State
    """

    TAX_BASES = [("ORIGIN", "Origin-based"), ("DESTINATION", "Destination-based")]

    abbreviation = USStateField(
        blank=False,
        null=False,
        primary_key=True,
        help_text="Abbreviation of State -> NY",
    )
    collects_saas_tax = models.BooleanField(
        default=False, help_text="If the State collects SaaS Tax"
    )
    tax_base = models.CharField(
        max_length=30,
        choices=TAX_BASES,
        default="DESTINATION",
        help_text="SaaS Tax Collection Method",
    )

    @classmethod
    def state_for_zip(cls, zip_code: str) -> StateType:
        """Get State for a given ZipCode string

        Args:
            zip_code (str): ZipCode to look up

        Returns:
            State: State that the given ZipCode belongs to
        """
        try:
            state = cls.objects.get(zipcodes=zip_code)
            return state
        except ObjectDoesNotExist:
            # nothing in DB, search USPS for it
            res = ZipService.lookup_zip(zip_code)
            # update db
            state = cls.objects.get(abbreviation=res.get("State"))
            return state

    def __str__(self):
        return f"State: {self.abbreviation}"


class ZipCode(models.Model):
    """Django Model for ZipCode

    """

    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="zipcodes",
        help_text="Foreign Key to the State the ZipCode is in",
    )
    code = models.CharField(
        max_length=9, primary_key=True, help_text="The 5 digit Zip Code"
    )
    tax_rate = models.DecimalField(
        blank=True,
        max_digits=5,
        decimal_places=4,
        null=True,
        help_text="Tax Rate for the given ZipCode -> 0.0625",
    )
    last_checked = models.DateTimeField(
        blank=True,
        null=True,
        help_text="DateTime of the last time the tax rate was refreshed",
    )

    @property
    def applicable_tax_rate(self) -> Decimal:
        """Calculates the applicable tax rate for a given ZipCode.

        Always use this over the the ZipCode's `tax_rate` field, becuase
        it takes into account tax nexues & Origin/Destination States to provide
        a true tax rate to charge.

        The function will return `0.00` if the state does not collect sales tax for SaaS.

        Note:
            If the given Zip Code is in a state where you hold a nexus and that state is an 
            ORIGIN-based sales tax state, the returned tax rate will be for the Zip Code of the nexus.

        Returns:
            Decimal: Tax Rate to charge for ZipCode (0.0625)
        """
        nexuses = ZipCode.nexuses()
        zcs = nexuses + [self]
        ZipCode.refresh_rates(zip_codes=zcs)
        self.refresh_from_db()

        for nexus in ZipCode.nexuses():
            if self.state == nexus.state and nexus.state.tax_base == "ORIGIN":
                return nexus.tax_rate
        # Destination Based
        return self.tax_rate if self.state.collects_saas_tax else Decimal("0.00")

    @classmethod
    def tax_rate_to_percentage(cls, tax_rate: Decimal) -> Decimal:
        """Converts tax rate to percentage

        Args:
            tax_rate (Decimal): Tax Rate

        Returns:
            Decimal: Tax Rate Percentage Example -> 6.2500
        """
        percentage = tax_rate * Decimal("100.00")
        return percentage.quantize(Decimal("0.0001"))

    @classmethod
    def get(cls, zip_code: str) -> ZipCodeType:
        """Get ZipCode Object for zip_code string.

        Always use this method to fetch ZipCodes, as it will
        get or create the ZipCode object.

        Args:
            zip_code (str): Zip Code to Query

        Returns:
            ZipCode: ZipCode Db Object
        """
        cls.validate(zip_code)
        try:
            return cls.objects.select_related("state").get(pk=zip_code)
        except ObjectDoesNotExist:
            state = State.state_for_zip(zip_code)
            return cls.objects.create(code=zip_code, state=state)

    @classmethod
    def nexuses(cls) -> List[ZipCodeType]:
        """Fetch Nexus ZipCodes

        Returns:
            List[ZipCode]: List of Nexus ZipCode Objects
        """
        return [
            cls.objects.get_or_create(
                pk=zc, defaults={"code": zc, "state": State.objects.get(pk=state)}
            )[0]
            for state, zc in settings.NEXUSES
        ]

    @classmethod
    def refresh_rates(cls, zip_codes: List[ZipCodeType], force=False) -> None:
        """Refresh Rates for a given list of ZipCode Objects.

        ZipCodes that are still inside the `TAX_RATE_INVALIDATE_INTERVAL`
        are skipped unless `force=True`.

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
    def validate(cls, zip_code: str) -> None:
        """Validates a Zip Code string

        Args:
            zip_code (str):

        Raises:
            InvalidZipCode:
        """
        if type(zip_code) is not str or len(zip_code) != 5 or not zip_code.isdecimal():
            raise InvalidZipCode
