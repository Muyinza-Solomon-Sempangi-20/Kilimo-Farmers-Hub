from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Alert
from market.models import MarketPrice


@login_required
def dashboard(request):
    profile = getattr(request.user, 'farmer_profile', None)
    user_district = profile.district if profile else ''

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
