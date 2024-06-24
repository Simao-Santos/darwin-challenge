from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
import requests_mock
from .models import CurrencyRate
from .views import parse_date, fetch_rate_from_api, get_rate_from_response, get_rate_average, get_interval_display_data
from decimal import Decimal
from datetime import datetime

class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_date_string = "2023-01-01"
        self.invalid_date_string = "20230101"
        self.endpoint = f"https://api.frankfurter.app/latest?to=USD"
        self.currency_data = {
            "amount": 1.0,
            "base": "EUR",
            "date": "2023-01-01",
            "rates": {"USD": 1.1234}
        }
        self.currency_rates = [
            CurrencyRate(rate_value=1.1234, rate_date="2023-01-01")
        ]

    def test_parse_date_valid(self):
        parsed_date = parse_date(self.test_date_string)
        self.assertEqual(parsed_date, datetime.strptime(self.test_date_string, '%Y-%m-%d').date())

    def test_parse_date_invalid(self):
        with self.assertRaises(ValidationError):
            parse_date(self.invalid_date_string)

    def test_fetch_rate_from_api(self):
        with requests_mock.Mocker() as m:
            m.get(self.endpoint, json=self.currency_data)
            data = fetch_rate_from_api(self.endpoint)
            self.assertEqual(data, self.currency_data)

    def test_fetch_rate_from_api_failure(self):
        with requests_mock.Mocker() as m:
            m.get(self.endpoint, status_code=404)
            with self.assertRaises(RuntimeError):
                fetch_rate_from_api(self.endpoint)

    def test_get_rate_from_response(self):
        rate, date = get_rate_from_response(self.currency_data)
        self.assertEqual(rate, 1.1234)
        self.assertEqual(date, datetime.strptime("2023-01-01", '%Y-%m-%d').date())

    def test_get_rate_from_response_missing_data(self):
        incomplete_data = {
            "amount": 1.0,
            "base": "EUR",
            "date": "2023-01-01",
            # "rates": {"USD": 1.1234}  # Missing rates key
        }
        with self.assertRaises(ValueError):
            get_rate_from_response(incomplete_data)

    def test_get_rate_average(self):
        average = get_rate_average(self.currency_rates)
        self.assertEqual(average, Decimal('1.123400'))

    def test_get_interval_display_data(self):
        display_data = get_interval_display_data("2023-01-01", "2023-01-02", self.currency_rates)
        expected_data = {
            'average_rate_value': Decimal('1.123400'),
            'start_date': "2023-01-01",
            'end_date': "2023-01-02"
        }
        self.assertEqual(display_data, expected_data)

    def test_get_latest_rate_view(self):
        url = reverse('currency-latest')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('rate_value', response.json())
        self.assertIn('rate_date', response.json())
        self.assertIsInstance(response.json()['rate_value'], float)
        self.assertIsInstance(response.json()['rate_date'], str)