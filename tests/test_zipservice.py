from django.test import TestCase

from taxtea import settings
from taxtea.services.usps import ZipService


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
