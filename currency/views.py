import logging
from django.db import IntegrityError
from django.http import JsonResponse
from django.core.exceptions import ValidationError
import requests
from decimal import Decimal
from datetime import datetime, timedelta, date

from .models import CurrencyRate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
FRANKFURTER_API_URL = 'https://api.frankfurter.app'
CURRENCY = "USD"
DATE_FORMAT = '%Y-%m-%d'
MIN_DATE = date(1999, 1, 4)

def home(request):
    return JsonResponse({})

def parse_date(date_string):
    try:
        return datetime.strptime(date_string, DATE_FORMAT).date()
    except ValueError:
        raise ValidationError(f"Invalid date format: {date_string}, expected format: {DATE_FORMAT}")

def fetch_rate_from_api(endpoint):
    try:
        response = requests.get(url=endpoint)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

def get_rate_from_response(data):
    try:
        rate = data['rates'][CURRENCY]
        date = parse_date(data['date'])
        return rate, date
    except KeyError as e:
        raise ValueError(f"Missing expected data in API response: {e}")

def get_latest_rate(request):
    today_date = datetime.now().date()
    latestCurrencyRate = CurrencyRate.objects.filter(rate_date=today_date).first()
    
    if latestCurrencyRate is not None:
        display_data = {
            'rate_value': latestCurrencyRate.rate_value,
            'rate_date': latestCurrencyRate.rate_date,
        }

        return JsonResponse(display_data)
    else:
        try:
            latest_endpoint = f"{FRANKFURTER_API_URL}/latest?to={CURRENCY}"
            data = fetch_rate_from_api(latest_endpoint)
            rate, date = get_rate_from_response(data)

            latest_currency_rate, _ = CurrencyRate.objects.get_or_create(
                rate_value=rate,
                rate_date=date,
            )

            display_data = {
                'rate_value': latest_currency_rate.rate_value,
                'rate_date': latest_currency_rate.rate_date,
            }

            return JsonResponse(display_data)

        except ValidationError as e:
            logger.error(f"Validation Error: {e}")
            return JsonResponse({'error': str(e)}, status=400)
        except (RuntimeError, ValueError, Exception):
            logger.error(f"An unexpected error occurred: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'})

def is_date_interval_in_db(start_date_string, end_date_string):
    try:
        start_date = parse_date(start_date_string)
        end_date = parse_date(end_date_string)
        if start_date > end_date or start_date < MIN_DATE:
            raise ValidationError("Start date must be before or equal to end date and after 04/01/1999.")

        # lista de datas do intervalo
        date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        
        # retorna datas presentes na base de dados
        currency = CurrencyRate.objects.filter(rate_date__in=date_list)
        currency_list = list(currency.values_list('rate_date', flat=True))
        
        # compara dias da base de dados com dias requisitados
        # se os dias estiverem todos na DB
        # retorna a lista de objs de CurrencyRate
        if set(date_list) == set(currency_list):
            return list(currency)
        else:
            return []
        
    except (ValueError, ValidationError) as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise

def get_rate_average(currency_rates_in_interval):
    if not currency_rates_in_interval:
        return Decimal('0.0')
    
    total = Decimal('0.0')
    for rate in currency_rates_in_interval:
        total += Decimal(str(rate.rate_value))
        
    average = total / Decimal(len(currency_rates_in_interval))
    return average.quantize(Decimal('0.000001'))

def get_interval_display_data(start_date, end_date, currency_rates_in_interval):
    average_rate_value = get_rate_average(currency_rates_in_interval)

    display_data = {
        'average_rate_value': average_rate_value,
        'start_date': start_date,
        'end_date': end_date
    }
    return display_data

def get_interval_rate(request, start_date_string, end_date_string):
    try:
        currency_rates_in_interval = is_date_interval_in_db(start_date_string, end_date_string)
        # if isinstance(currency_rates_in_interval, str):
        #     error_string = currency_rates_in_interval
        #     return JsonResponse({'error': error_string}, status=400)
        if currency_rates_in_interval:
            display_data = get_interval_display_data(start_date_string, end_date_string, currency_rates_in_interval)

            return JsonResponse(display_data)
        else:
            interval_endpoint = f"{FRANKFURTER_API_URL}/{start_date_string}..{end_date_string}?to={CURRENCY}"
            data = fetch_rate_from_api(interval_endpoint)

            # Extract USD values from the rates dictionary
            start_date = data['start_date']
            end_date = data['end_date']
            currency_rate_list = []
            for date_string, currencies in data['rates'].items():
                currency_value = currencies.get(CURRENCY)
                if currency_value is not None:
                    date = parse_date(date_string)
                    currency_rate_list.append(CurrencyRate(rate_value=currency_value, rate_date=date))
            
            try:
                currency_rates_in_interval = CurrencyRate.objects.bulk_create(currency_rate_list, ignore_conflicts=True)
            except IntegrityError as e:
                logger.error(f"Database integrity error: {e}")
                return JsonResponse({'error': 'An unexpected error occurred'})
                
            display_data = get_interval_display_data(start_date, end_date, currency_rates_in_interval)

            return JsonResponse(display_data)
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    except (RuntimeError, ValueError, Exception) as e:
        logger.error(f"An unexpected error occurred: {e}")
        return JsonResponse({'error': 'An unexpected error occurred'})