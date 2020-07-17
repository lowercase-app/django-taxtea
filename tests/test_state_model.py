from unittest.mock import patch

from django.test import TestCase
from model_bakery import baker

from taxtea.models import State


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
