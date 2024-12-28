# weather_app/views.py

from django.shortcuts import render
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def index(request):
    weather_data = None
    error_message = None
    if 'place' in request.GET:
        place = request.GET['place']
        weather_data, error_message = get_weather_data(place)
    return render(request, 'index.html', {'weather_data': weather_data, 'error_message': error_message})

def get_weather_data(place):
    api_key = settings.TOMORROW_IO_API_KEY
    url = 'https://api.tomorrow.io/v4/timelines'
    headers = {
        'Content-Type': 'application/json',
        'apikey': api_key
    }
    params = {
        'location': place,
        'fields': [
            'temperature',
            'temperatureApparent',
            'pressureSurfaceLevel',
            'pressureSeaLevel',
            'precipitationIntensity',
            'humidity',
            'windSpeed',
            'windDirection',
            'rainIntensity',
            'snowIntensity'
        ],
        'timesteps': '1h',
        'units': 'metric',
        'startTime': 'now',
        'endTime': 'nowPlus5d'  # Adjust endTime to be within 5 days
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        logger.info(data)  # Log the API response
        intervals = data['data']['timelines'][0]['intervals']  # Adjust as per the actual response structure
        weather_data = {
            'place': place,
            'temperature': intervals[0]['values']['temperature'],
            'temperatureApparent': intervals[0]['values']['temperatureApparent'],
            'pressureSurfaceLevel': intervals[0]['values']['pressureSurfaceLevel'],
            'pressureSeaLevel': intervals[0]['values']['pressureSeaLevel'],
            'precipitationIntensity': intervals[0]['values']['precipitationIntensity'],
            'humidity': intervals[0]['values']['humidity'],
            'windSpeed': intervals[0]['values']['windSpeed'],
            'windDirection': intervals[0]['values']['windDirection'],
            'rainIntensity': intervals[0]['values']['rainIntensity'],
            'snowIntensity': intervals[0]['values']['snowIntensity']
        }
        return weather_data, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None, 'Failed to retrieve weather data. Please try again.'

def compare(request):
    if request.method == 'POST':
        num_places = int(request.POST.get('num_places', 2))
        places = [request.POST.get(f'place_{i+1}') for i in range(num_places)]
        weather_data_list = []
        for place in places:
            weather_data, error_message = get_weather_data(place)
            if weather_data:
                weather_data_list.append(weather_data)
            else:
                weather_data_list.append({'place': place, 'error': error_message})
        
        return render(request, 'compare.html', {'weather_data_list': weather_data_list, 'num_places': num_places})
    return render(request, 'compare.html')