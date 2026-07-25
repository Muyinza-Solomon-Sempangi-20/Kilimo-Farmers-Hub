from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from .models import Alert
from market.models import MarketPrice


@login_required
def dashboard(request):
    profile = getattr(request.user, 'farmer_profile', None)
    user_district = profile.district if profile else ''

    # Location-specific alerts
    alerts = Alert.objects.filter(is_active=True)
    if user_district:
        alerts = alerts.filter(
            models.Q(district__iexact=user_district) | models.Q(district='')
        )
    else:
        alerts = alerts.filter(district='')
    alerts = alerts[:5]

    prices = MarketPrice.objects.order_by('-recorded_at')[:4]
    return render(request, 'core/dashboard.html', {
        'alerts': alerts,
        'prices': prices,
        'user_district': user_district,
    })


def landing(request):
    return render(request, 'core/landing.html')


def seed_alerts(request):
    """One-time endpoint to seed disease alerts. Remove after use."""
    DISTRICT_ALERTS = [
        {"title": "Fall Armyworm outbreak in Maize", "body": "High Fall Armyworm activity reported in Central Uganda. Scout maize whorls for larvae and frass. Treat with Emamectin benzoate (0.5g/L) at dusk.", "severity": "danger", "district": "mukono"},
        {"title": "Coffee Wilt Disease confirmed", "body": "Coffee Wilt Disease detected in Robusta coffee farms in Mukono. Uproot and burn infected trees. Report to UCDA.", "severity": "danger", "district": "mukono"},
        {"title": "Fall Armyworm activity elevated", "body": "Fall Armyworm detected in multiple maize fields in Kampala. Inspect whorls for caterpillars. Apply Emamectin benzoate.", "severity": "warning", "district": "kampala"},
        {"title": "Banana Xanthomonas Wilt alert", "body": "Banana Xanthomonas Wilt spreading in Wakiso banana farms. Remove entire infected mats. Disinfect tools with JIK.", "severity": "danger", "district": "wakiso"},
        {"title": "Bean Anthracnose risk", "body": "Wet conditions favoring Bean Anthracnose in Wakiso. Use certified seed and apply copper-based fungicide.", "severity": "warning", "district": "wakiso"},
        {"title": "Tomato Late Blight warning", "body": "Late Blight reported in Masaka tomato farms. Apply Metalaxyl + Mancozeb. Remove affected leaves immediately.", "severity": "warning", "district": "masaka"},
        {"title": "Cassava Mosaic Disease spread", "body": "Cassava Mosaic Disease spreading in Jinja. Remove infected plants and control whitefly vectors. Plant resistant varieties.", "severity": "danger", "district": "jinja"},
        {"title": "Fall Armyworm in Eastern maize", "body": "Fall Armyworm detected across Mbale maize fields. Spray Emamectin benzoate into whorl.", "severity": "warning", "district": "mbale"},
        {"title": "Bean Root Rot after rains", "body": "Bean Root Rot appearing in Soroti after heavy rains. Improve drainage and use seed treatment.", "severity": "warning", "district": "soroti"},
        {"title": "Cassava Brown Streak Disease", "body": "Cassava Brown Streak Disease confirmed in Tororo. Remove and burn infected plants. Use resistant varieties.", "severity": "danger", "district": "tororo"},
        {"title": "Fall Armyworm in Northern maize", "body": "Fall Armyworm activity increasing in Gulu. Scout fields weekly. Treat early with Emamectin benzoate.", "severity": "warning", "district": "gulu"},
        {"title": "Groundnut Rust risk", "body": "Humid conditions favoring Groundnut Rust in Lira. Apply Propiconazole at first sign.", "severity": "info", "district": "lira"},
        {"title": "Sorghum Midge alert", "body": "Sorghum Midge causing grain sterility in Arua. Spray Dimethoate during flowering period.", "severity": "warning", "district": "arua"},
        {"title": "Coffee Berry Disease risk", "body": "Coffee Berry Disease risk high in Mbarara coffee farms. Apply Copper Hydroxide before flowering.", "severity": "warning", "district": "mbarara"},
        {"title": "Banana Black Sigatoka", "body": "Black Sigatoka detected in Fort Portal banana plantations. Remove infected leaves. Apply fungicide.", "severity": "danger", "district": "fort portal"},
        {"title": "Late Blight in Irish Potatoes", "body": "Late Blight threatening Irish Potato crops in Kabale. Apply Metalaxyl + Mancozeb.", "severity": "danger", "district": "kabale"},
        {"title": "Maize Gray Leaf Spot", "body": "Grey Leaf Spot appearing in Hoima maize fields. Apply Mancozeb (2.5g/L).", "severity": "warning", "district": "hoima"},
        {"title": "Fall Armyworm nationwide advisory", "body": "Fall Armyworm remains active across Uganda. Scout fields weekly and treat early.", "severity": "info", "district": ""},
        {"title": "MAAIF livestock vaccination drive", "body": "Ministry conducting FMD and Rift Valley Fever vaccination. Contact your district vet officer.", "severity": "info", "district": ""},
    ]

    if Alert.objects.filter(category='disease').exists():
        return JsonResponse({"status": "already_seeded", "alerts": Alert.objects.filter(category='disease').count()})

    count = 0
    for a in DISTRICT_ALERTS:
        Alert.objects.create(
            title=a['title'], body=a['body'], severity=a['severity'],
            category='disease', district=a['district'],
            source='Kilimo Hub', is_active=True,
        )
        count += 1

    return JsonResponse({"status": "seeded", "alerts": count})


def clear_weather_cache(request):
    """One-time endpoint to clear weather cache."""
    from weather.models import WeatherCache
    count = WeatherCache.objects.count()
    WeatherCache.objects.all().delete()
    return JsonResponse({"status": "cleared", "deleted": count})
