from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Market, Commodity, MarketPrice


@login_required
def price_list(request):
    commodity_name = request.GET.get('commodity', '')
    district_filter = request.GET.get('district', '')
    commodities = Commodity.objects.all()
    markets = Market.objects.all()

    # Auto-detect district from profile
    if not district_filter:
        profile = getattr(request.user, 'farmer_profile', None)
        if profile and profile.district:
            district_filter = profile.district

    # Filter markets by district if available
    if district_filter:
        markets = Market.objects.filter(district__icontains=district_filter)

    if commodity_name:
        try:
            commodity = Commodity.objects.get(name__iexact=commodity_name)
            prices = MarketPrice.objects.filter(commodity=commodity, market__in=markets).select_related('market').order_by('-recorded_at')[:20]
        except Commodity.DoesNotExist:
            commodity = None
            prices = MarketPrice.objects.filter(market__in=markets).select_related('market', 'commodity').order_by('-recorded_at')[:20]
    else:
        commodity = None
        prices = MarketPrice.objects.filter(market__in=markets).select_related('market', 'commodity').order_by('-recorded_at')[:20]

    return render(request, 'market/prices.html', {
        'prices': prices,
        'commodities': commodities,
        'selected_commodity': commodity,
        'district_filter': district_filter,
        'all_districts': Market.objects.values_list('district', flat=True).distinct(),
    })


@login_required
def market_list(request):
    profile = getattr(request.user, 'farmer_profile', None)
    user_district = profile.district if profile else ''
    markets = Market.objects.all()
    if user_district:
        nearby = markets.filter(district__icontains=user_district)
        other = markets.exclude(district__icontains=user_district)
    else:
        nearby = Market.objects.none()
        other = markets
    return render(request, 'market/markets.html', {
        'nearby_markets': nearby,
        'other_markets': other,
        'user_district': user_district,
    })
