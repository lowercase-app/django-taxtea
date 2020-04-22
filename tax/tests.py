from unittest.mock import MagicMock
from django.test import TestCase
from tax.models import State, ZipCode
from tax.services.usps import ZipService

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
    def test_return(self):
        ZipService.lookup_zips = MagicMock(return_value=)
