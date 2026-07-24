import json
import requests
from datetime import datetime, timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone as dj_timezone
from .models import WeatherCache

DISTRICT_COORDS = {
    'Kampala':     (-0.3476, 32.5825),
    'Mukono':      (0.3536,  32.7550),
    'Wakiso':      (0.4017,  32.4580),
    'Jinja':       (0.4244,  33.2041),
    'Gulu':        (2.7748,  32.2990),
    'Lira':        (2.2499,  32.8997),
    'Mbarara':     (-0.6072, 30.6545),
    'Arua':        (3.0200,  30.9114),
    'Soroti':      (1.7148,  33.6109),
    'Masaka':      (-0.3333, 31.7333),
    'Mbale':       (1.0796,  34.1753),
    'Fort Portal': (0.6710,  30.2750),
    'Kabale':      (-1.2490, 29.9891),
    'Tororo':      (0.6926,  34.1815),
    'Hoima':       (1.4330,  31.3522),
}

ICON_MAP = {
    '01': 'Clear',     '02': 'Partly cloudy',
    '03': 'Cloudy',    '04': 'Overcast',
    '09': 'Showers',   '10': 'Rain',
    '11': 'Thunderstorm', '13': 'Snow',
    '50': 'Misty',
}

WEATHER_SVG = {
    'Clear':        "sun",
    'Partly cloudy':"cloud-sun",
    'Cloudy':       "cloud",
    'Overcast':     "cloud",
    'Showers':      "cloud-rain",
    'Rain':         "cloud-rain",
    'Thunderstorm': "storm",
    'Snow':         "snowflake",
    'Misty':        "mist",
}

def get_icon_code(icon_str):
    """e.g. '01d' -> 'Clear'"""
    prefix = icon_str[:2] if icon_str else '01'
    return ICON_MAP.get(prefix, 'Partly cloudy')

def build_farming_advisory(forecast_days):
    """Generate a simple planting/farming advisory from the forecast."""
    total_rain = sum(d.get('rain_mm', 0) for d in forecast_days[:3])
    max_temp   = max(d.get('temp_hi', 25) for d in forecast_days[:3])
    has_storm  = any(d.get('desc') == 'Thunderstorm' for d in forecast_days[:3])

    if has_storm:
        return "Thunderstorms forecast in the next 3 days. Avoid field operations and stay away from tall trees. Delay any spraying or fertilizer application."
    elif total_rain > 30:
        return "Heavy rainfall expected this week. Good conditions for transplanting seedlings. Delay fertilizer and pesticide applications until after the rains to prevent runoff losses."
    elif total_rain > 10:
        return "Moderate rains expected. Good for planting. Apply fertilizer before rain for best uptake. Scout fields for waterlogging in low-lying areas."
    elif max_temp > 32:
        return "Hot and dry conditions ahead. Irrigate crops if possible. Mulch around plants to conserve soil moisture. Harvest mature crops before heat stress sets in."
    else:
        return "Favorable conditions for most field operations. Good week for land preparation, weeding, and pesticide application."

def fetch_from_owm(district):
    """Fetch live data from OpenWeatherMap One Call API."""
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key or api_key == 'demo':
        return None

    coords = DISTRICT_COORDS.get(district, DISTRICT_COORDS['Mukono'])
    lat, lon = coords

    try:
        # Current weather
        current_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        )
        cur_resp = requests.get(current_url, timeout=8)
        cur_resp.raise_for_status()
        cur = cur_resp.json()

        # 5-day / 3-hour forecast
        forecast_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?lat={lat}&lon={lon}&appid={api_key}&units=metric&cnt=40"
        )
        fc_resp = requests.get(forecast_url, timeout=8)
        fc_resp.raise_for_status()
        fc_data = fc_resp.json()

        # Process current
        wind_speed  = round(cur['wind']['speed'] * 3.6)  # m/s to km/h
        wind_deg    = cur['wind'].get('deg', 0)
        directions  = ['N','NE','E','SE','S','SW','W','NW']
        wind_dir    = directions[round(wind_deg / 45) % 8]
        icon_code   = get_icon_code(cur['weather'][0]['icon'])

        current = {
            'temp':     round(cur['main']['temp']),
            'feels_like': round(cur['main']['feels_like']),
            'desc':     icon_code,
            'humidity': cur['main']['humidity'],
            'wind':     f"{wind_speed} km/h {wind_dir}",
            'pressure': cur['main']['pressure'],
            'visibility': round(cur.get('visibility', 10000) / 1000, 1),
        }

        # Group 3-hourly into daily
        daily = {}
        for item in fc_data['list']:
            dt   = datetime.fromtimestamp(item['dt'], tz=timezone.utc)
            day  = dt.strftime('%a')
            date = dt.strftime('%Y-%m-%d')
            key  = date
            rain = item.get('rain', {}).get('3h', 0)
            if key not in daily:
                daily[key] = {
                    'day':     day,
                    'temp_hi': item['main']['temp_max'],
                    'temp_lo': item['main']['temp_min'],
                    'desc':    get_icon_code(item['weather'][0]['icon']),
                    'rain_mm': rain,
                }
            else:
                daily[key]['temp_hi'] = max(daily[key]['temp_hi'], item['main']['temp_max'])
                daily[key]['temp_lo'] = min(daily[key]['temp_lo'], item['main']['temp_min'])
                daily[key]['rain_mm'] = round(daily[key]['rain_mm'] + rain, 1)

        forecast_days = []
        for v in list(daily.values())[:7]:
            forecast_days.append({
                'day':     v['day'],
                'temp_hi': round(v['temp_hi']),
                'temp_lo': round(v['temp_lo']),
                'desc':    v['desc'],
                'rain_mm': round(v['rain_mm'], 1),
            })

        advisory = build_farming_advisory(forecast_days)

        return {
            'location': f"{district}, Uganda",
            'current':  current,
            'forecast': forecast_days,
            'advisory': advisory,
            'source':   'live',
            'fetched_at': datetime.now(timezone.utc).isoformat(),
        }

    except requests.RequestException as e:
        print(f"[WeatherAPI] Error fetching for {district}: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"[WeatherAPI] Parse error for {district}: {e}")
        return None

def get_weather(district):
    """
    Return weather data for a district.
    Uses cache (3-hour TTL) to avoid hammering the API.
    Falls back to mock data if API key missing or request fails.
    """
    from datetime import timedelta

    cache_obj = WeatherCache.objects.filter(district=district).first()
    if cache_obj:
        age = dj_timezone.now() - cache_obj.updated_at
        if age < timedelta(hours=3):
            data = json.loads(cache_obj.data_json)
            data['from_cache'] = True
            return data

    # Try live fetch
    live = fetch_from_owm(district)
    if live:
        if cache_obj:
            cache_obj.data_json = json.dumps(live)
            cache_obj.save()
        else:
            WeatherCache.objects.create(district=district, data_json=json.dumps(live))
        live['from_cache'] = False
        return live

    # Fallback to stale cache if available
    if cache_obj:
        data = json.loads(cache_obj.data_json)
        data['from_cache'] = True
        data['stale'] = True
        return data

    # Last resort mock
    return {
        'location': f"{district}, Uganda",
        'source': 'mock',
        'from_cache': False,
        'current': {'temp': 26, 'feels_like': 25, 'desc': 'Partly cloudy',
                    'humidity': 72, 'wind': '12 km/h NE', 'pressure': 1013, 'visibility': 10},
        'forecast': [
            {'day': 'Today', 'temp_hi': 26, 'temp_lo': 18, 'desc': 'Partly cloudy', 'rain_mm': 0},
            {'day': 'Tomorrow', 'temp_hi': 24, 'temp_lo': 17, 'desc': 'Rain', 'rain_mm': 12},
        ],
        'advisory': 'Configure your OPENWEATHER_API_KEY in .env to see live weather data.',
    }


@login_required
def weather_home(request):
    district = request.GET.get('district', '')
    
    # If no district specified, use the user's profile district
    if not district:
        profile = getattr(request.user, 'farmer_profile', None)
        if profile and profile.district:
            # Capitalize to match DISTRICT_COORDS keys
            district = profile.district.capitalize()
    
    if district not in DISTRICT_COORDS:
        district = 'Mukono'
    
    forecast = get_weather(district)
    districts = list(DISTRICT_COORDS.keys())
    return render(request, 'weather/home.html', {
        'forecast': forecast,
        'district': district,
        'districts': districts,
        'WEATHER_SVG': WEATHER_SVG,
    })
