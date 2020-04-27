from unittest.mock import patch
from django.test import TestCase
from model_bakery import baker
from tax.models import State, ZipCode
from tax.services.usps import ZipService
from tax import settings
from tax.core import state_for_zip, determine_tax_method_and_rate

# Create your tests here.


class TestStateModel(TestCase):
    """
    Test State Django Model
    """

    # @classmethod
    # def setUpTestData(cls):
    #     State.objects.create(abbreviation="OH", collects_saas_tax=True)
    #     State.objects.create(abbreviation="AS", collects_saas_tax=False)
    #     pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dunder_str(self):
        ohio = State.objects.get(abbreviation="OH")
        self.assertEqual(ohio.__str__(), "State: OH")


class TestZipCodeModel(TestCase):
    """
    Test ZipCode Django Model
    """

    @classmethod
    def setUpTestData(cls):
        ZipCode.objects.create(code="44136", state=State.objects.get(abbreviation="OH"))

    def test_zip_needs_state(self):
        from django.db.utils import IntegrityError

        with self.assertRaises(IntegrityError):
            ZipCode.objects.create(code="11111")

    def test_dunder_str(self):
        z = ZipCode.objects.get(pk="44136")
        self.assertEqual(z.__str__(), f"ZipCode: 44136, State: OH")


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


class TestCore(TestCase):
    def setUp(self):
        self.zipcode = baker.make("tax.ZipCode", code="27587", state__abbreviation="NC")
        self.zipcode_pa = baker.make(
            "tax.ZipCode",
            code="19012",
            state__abbreviation="PA",
            state__tax_base="ORIGIN",
        )
        self.zipcode_origin = baker.make(
            "tax.ZipCode",
            code="15216",
            state__abbreviation="PA",
            state__tax_base="ORIGIN",
        )

    @patch("tax.core.ZipService")
    def test_state_for_zip(self, mock_zip_service):
        mock_zip_service.lookup_zip = self.zipcode
        self.assertEqual(state_for_zip("27587"), State.objects.get(abbreviation="NC"))

    def test_determine_tax_method_and_rate_destination(self):
        method, rate = determine_tax_method_and_rate(self.zipcode)
        self.assertEqual(method, "DESTINATION")
        self.assertEqual(rate, self.zipcode.tax_rate)

    @patch("tax.models.ZipCode")
    def test_determine_tax_method_and_rate_origin(self, mock_ZipCode):
        mock_ZipCode.origins = [self.zipcode_origin]
        method, rate = determine_tax_method_and_rate(self.zipcode_pa)

        self.assertEqual(method, "ORIGIN")
        self.assertEqual(rate, self.zipcode_origin.tax_rate)
