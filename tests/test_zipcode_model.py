from decimal import Decimal

from django.test import TestCase
from model_bakery import baker

from taxtea.models import State, ZipCode


class TestZipCodeModel(TestCase):
    """
    Test ZipCode Django Model
    """

    @classmethod
    def setUpTestData(cls):
        ZipCode.objects.create(code="44136", state=State.objects.get(abbreviation="OH"))

    def setUp(self):
        self.zipcode = baker.make(
            "taxtea.ZipCode",
            code="27587",
            tax_rate=Decimal(0.06),
            state__abbreviation="NC",
            state__tax_base="DESTINATION",
        )
        self.zipcode_pa = baker.make(
            "taxtea.ZipCode",
            code="19012",
            tax_rate=Decimal(0.08),
            state__abbreviation="PA",
            state__tax_base="ORIGIN",
            state__collects_saas_tax=True,
        )
        self.zipcode_nexus = baker.make(
            "taxtea.ZipCode",
            code="15216",
            tax_rate=Decimal(0.07),
            state__abbreviation="PA",
            state__tax_base="ORIGIN",
            state__collects_saas_tax=True,
        )

    def test_zip_needs_state(self):
        from django.db.utils import IntegrityError

        with self.assertRaises(IntegrityError):
            ZipCode.objects.create(code="11111")

    def test_dunder_str(self):
        z = ZipCode.objects.get(pk="44136")
        self.assertEqual(z.__str__(), f"ZipCode: 44136, State: OH")

    def test_get(self):
        self.assertEqual(ZipCode.get("44136"), ZipCode.objects.get(pk="44136"))

    def test_applicable_tax_rate(self):

        self.assertEqual(self.zipcode.applicable_tax_rate, Decimal(0.00))
