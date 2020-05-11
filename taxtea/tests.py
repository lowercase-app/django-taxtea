from unittest.mock import patch
from django.test import TestCase
from model_bakery import baker
from taxtea.models import State, ZipCode
from taxtea.services.usps import ZipService
from taxtea import settings
from decimal import Decimal

# Create your tests here.


class TestStateModel(TestCase):
    """
    Test State Django Model
    """

    def setUp(self):
        self.zip_code = baker.make(
            "taxtea.ZipCode", code="27587", state__abbreviation="NC"
        )

    def tearDown(self):
        pass

    def test_dunder_str(self):
        ohio = State.objects.get(abbreviation="OH")
        self.assertEqual(ohio.__str__(), "State: OH")

    @patch("taxtea.models.ZipService")
    def test_state_for_zip(self, mock_zip_service):
        mock_zip_service.lookup_zip = self.zip_code
        self.assertEqual(
            State.state_for_zip("27587"), State.objects.get(abbreviation="NC")
        )


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


class TestZipService(TestCase):
    def test_generate_xml_payload_single_zip(self):
        self.assertEqual(
            ZipService._generate_xml_payload(["44136"]),
            f'<?xml version="1.0" encoding="utf-8"?>\n<CityStateLookupRequest USERID="{settings.USPS_USER}"><ZipCode><Zip5>44136</Zip5></ZipCode></CityStateLookupRequest>',
        )

    def test_generate_xml_payload_invalid_params(self):
        with self.assertRaises(TypeError):
            ZipService._generate_xml_payload("44136")

    def test_generate_xml_payload_multiple_zips(self):
        self.assertEqual(
            ZipService._generate_xml_payload(["44136", "44149"]),
            f'<?xml version="1.0" encoding="utf-8"?>\n<CityStateLookupRequest USERID="{settings.USPS_USER}"><ZipCode><Zip5>44136</Zip5></ZipCode><ZipCode><Zip5>44149</Zip5></ZipCode></CityStateLookupRequest>',
        )
