import math
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

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


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def find_nearest_district(lat, lon):
    """Find the nearest Ugandan district for given coordinates."""
    best = None
    best_dist = float('inf')
    for district, (dlat, dlon) in DISTRICT_COORDS.items():
        dist = haversine(lat, lon, dlat, dlon)
        if dist < best_dist:
            best_dist = dist
            best = district
    return best, round(best_dist, 1)


@login_required
@require_POST
def detect_location(request):
    """
    Accept GPS coordinates from the browser and return the nearest district.
    POST {lat, lon}  OR  POST {district: "Kampala"}
    """
    try:
        data = json.loads(request.body)

        # Manual district selection
        district_name = data.get('district', '').strip()
        if district_name:
            # Capitalize first letter to match DISTRICT_COORDS keys
            district_name = district_name.strip().title()
            if district_name in DISTRICT_COORDS:
                profile = getattr(request.user, 'farmer_profile', None)
                if profile:
                    profile.district = district_name.lower()
                    profile.save()
                return JsonResponse({
                    'district': district_name,
                    'distance_km': 0,
                })

        # GPS coordinates
        lat = float(data.get('lat', 0))
        lon = float(data.get('lon', 0))

        if not (-5 < lat < 5 and 29 < lon < 35):
            return JsonResponse({'error': 'Coordinates outside Uganda'}, status=400)

        district, distance_km = find_nearest_district(lat, lon)

        # Save to profile
        profile = getattr(request.user, 'farmer_profile', None)
        if profile:
            profile.district = district.lower()
            profile.save()

        return JsonResponse({
            'district': district,
            'distance_km': distance_km,
            'lat': lat,
            'lon': lon,
        })
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)
