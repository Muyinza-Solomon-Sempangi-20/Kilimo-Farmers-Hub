from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from market.models import Market, Commodity, MarketPrice


MARKETS = [
    {"name": "St. Balikuddembe (Owino)", "district": "kampala", "region": "Central", "lat": 0.3136, "lon": 32.5811},
    {"name": "Nakasero Market", "district": "kampala", "region": "Central", "lat": 0.3183, "lon": 32.5855},
    {"name": "Kasubi Market", "district": "kampala", "region": "Central", "lat": 0.3300, "lon": 32.5550},
    {"name": "Kikuubo Market", "district": "kampala", "region": "Central", "lat": 0.3100, "lon": 32.5800},
    {"name": "Lugogo Market", "district": "kampala", "region": "Central", "lat": 0.3200, "lon": 32.5900},
    {"name": "Owino Olwol Market", "district": "mukono", "region": "Central", "lat": 0.3536, "lon": 32.7550},
    {"name": "Mukono Town Market", "district": "mukono", "region": "Central", "lat": 0.3530, "lon": 32.7560},
    {"name": "Ggaba Market", "district": "kampala", "region": "Central", "lat": 0.3050, "lon": 32.6000},
    {"name": "Wakiso Market", "district": "wakiso", "region": "Central", "lat": 0.4017, "lon": 32.4580},
    {"name": "Kawaala Market", "district": "kampala", "region": "Central", "lat": 0.3350, "lon": 32.5600},
    {"name": "Jinja Main Market", "district": "jinja", "region": "Eastern", "lat": 4.4244, "lon": 33.2041},
    {"name": "Owino Market Jinja", "district": "jinja", "region": "Eastern", "lat": 4.4200, "lon": 33.2100},
    {"name": "Mbale Town Market", "district": "mbale", "region": "Eastern", "lat": 1.0796, "lon": 34.1753},
    {"name": "Soroti Market", "district": "soroti", "region": "Eastern", "lat": 1.7148, "lon": 33.6109},
    {"name": "Tororo Market", "district": "tororo", "region": "Eastern", "lat": 0.6926, "lon": 34.1815},
    {"name": "Gulu Main Market", "district": "gulu", "region": "Northern", "lat": 2.7748, "lon": 32.2990},
    {"name": "Lira Town Market", "district": "lira", "region": "Northern", "lat": 2.2499, "lon": 32.8997},
    {"name": "Arua Market", "district": "arua", "region": "Northern", "lat": 3.0200, "lon": 30.9114},
    {"name": "Mbarara Market", "district": "mbarara", "region": "Western", "lat": -0.6072, "lon": 30.6545},
    {"name": "Fort Portal Market", "district": "fort portal", "region": "Western", "lat": 0.6710, "lon": 30.2750},
    {"name": "Kabale Market", "district": "kabale", "region": "Western", "lat": -1.2490, "lon": 29.9891},
    {"name": "Hoima Market", "district": "hoima", "region": "Western", "lat": 1.4330, "lon": 31.3522},
    {"name": "Masaka Town Market", "district": "masaka", "region": "Central", "lat": -0.3333, "lon": 31.7333},
    {"name": "Entebbe Market", "district": "wakiso", "region": "Central", "lat": 0.0564, "lon": 32.4622},
    {"name": "Ntinda Market", "district": "kampala", "region": "Central", "lat": 0.3380, "lon": 32.5930},
]

COMMODITIES = [
    {"name": "Maize", "local_name": "Emere", "category": "crop", "unit": "kg"},
    {"name": "Beans", "local_name": "Obugobe", "category": "crop", "unit": "kg"},
    {"name": "Coffee", "local_name": "Kawuwa", "category": "crop", "unit": "kg"},
    {"name": "Banana", "local_name": "Gonja", "category": "crop", "unit": "bunch"},
    {"name": "Cassava", "local_name": "Muwogo", "category": "crop", "unit": "kg"},
    {"name": "Sweet Potato", "local_name": "Lumonde", "category": "crop", "unit": "kg"},
    {"name": "Rice", "local_name": "Mucumbe", "category": "crop", "unit": "kg"},
    {"name": "Millet", "local_name": "Kalo", "category": "crop", "unit": "kg"},
    {"name": "Sorghum", "local_name": "Jowero", "category": "crop", "unit": "kg"},
    {"name": "Groundnuts", "local_name": "Nbongo", "category": "crop", "unit": "kg"},
    {"name": "Sesame", "local_name": "Kujuju", "category": "crop", "unit": "kg"},
    {"name": "Cabbage", "local_name": "Kabage", "category": "crop", "unit": "kg"},
    {"name": "Tomatoes", "local_name": "Ntula", "category": "crop", "unit": "kg"},
    {"name": "Onions", "local_name": "Tungulu", "category": "crop", "unit": "kg"},
    {"name": "Matooke", "local_name": "Matooke", "category": "crop", "unit": "bunch"},
    {"name": "Irish Potato", "local_name": "Irish", "category": "crop", "unit": "kg"},
    {"name": "Livestock", "local_name": "Ng'ombe", "category": "livestock", "unit": "head"},
    {"name": "Goat", "local_name": "Embuzi", "category": "livestock", "unit": "head"},
    {"name": "Chicken", "local_name": "Enkoko", "category": "livestock", "unit": "head"},
    {"name": "Fish (Tilapia)", "local_name": "Enge", "category": "livestock", "unit": "kg"},
]

# Realistic price ranges per commodity in UGX (based on Uganda market data)
PRICE_RANGES = {
    "Maize":         {"min": 1200, "max": 2200, "avg": 1650},
    "Beans":         {"min": 2800, "max": 4500, "avg": 3500},
    "Coffee":        {"min": 6000, "max": 9500, "avg": 7800},
    "Banana":        {"min": 8000, "max": 15000, "avg": 12000},
    "Cassava":       {"min": 800, "max": 1500, "avg": 1100},
    "Sweet Potato":  {"min": 1000, "max": 2000, "avg": 1400},
    "Rice":          {"min": 3500, "max": 6000, "avg": 4800},
    "Millet":        {"min": 2500, "max": 4000, "avg": 3200},
    "Sorghum":       {"min": 1800, "max": 3000, "avg": 2300},
    "Groundnuts":    {"min": 4000, "max": 7000, "avg": 5500},
    "Sesame":        {"min": 5000, "max": 8000, "avg": 6500},
    "Cabbage":       {"min": 1500, "max": 3000, "avg": 2000},
    "Tomatoes":      {"min": 2000, "max": 4500, "avg": 3000},
    "Onions":        {"min": 3000, "max": 5500, "avg": 4200},
    "Matooke":       {"min": 15000, "max": 25000, "avg": 18000},
    "Irish Potato":  {"min": 1500, "max": 3000, "avg": 2200},
    "Livestock":     {"min": 800000, "max": 1500000, "avg": 1100000},
    "Goat":          {"min": 150000, "max": 350000, "avg": 250000},
    "Chicken":       {"min": 25000, "max": 55000, "avg": 40000},
    "Fish (Tilapia)": {"min": 8000, "max": 14000, "avg": 11000},
}

# Region price adjustments (some regions are cheaper/more expensive)
REGION_ADJUST = {
    "Central": 1.0,
    "Eastern": 0.92,
    "Northern": 0.88,
    "Western": 0.95,
}


class Command(BaseCommand):
    help = 'Seed the database with realistic Ugandan market prices'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            MarketPrice.objects.all().delete()
            Market.objects.all().delete()
            Commodity.objects.all().delete()
            self.stdout.write('Cleared existing data.')

        # Create markets
        markets_created = 0
        for m in MARKETS:
            obj, created = Market.objects.get_or_create(
                name=m["name"],
                defaults={
                    "district": m["district"],
                    "region": m["region"],
                    "latitude": m["lat"],
                    "longitude": m["lon"],
                }
            )
            if created:
                markets_created += 1
        self.stdout.write(f'Created {markets_created} markets (total: {Market.objects.count()})')

        # Create commodities
        commodities_created = 0
        for c in COMMODITIES:
            obj, created = Commodity.objects.get_or_create(
                name=c["name"],
                defaults={
                    "local_name": c["local_name"],
                    "category": c["category"],
                    "unit": c["unit"],
                }
            )
            if created:
                commodities_created += 1
        self.stdout.write(f'Created {commodities_created} commodities (total: {Commodity.objects.count()})')

        # Create prices for each commodity at each market
        now = timezone.now()
        prices_created = 0
        all_markets = list(Market.objects.all())
        all_commodities = list(Commodity.objects.all())

        for commodity in all_commodities:
            price_range = PRICE_RANGES.get(commodity.name, {"min": 1000, "max": 5000, "avg": 2500})

            for market in all_markets:
                # Skip if price already exists for this combo
                if MarketPrice.objects.filter(commodity=commodity, market=market).exists():
                    continue

                # Region adjustment
                adj = REGION_ADJUST.get(market.region, 1.0)
                base_price = price_range["avg"] * adj

                # Add some random variation
                variation = random.uniform(0.85, 1.15)
                price = round(base_price * variation, -1)
                price_min = round(price * 0.9, -1)
                price_max = round(price * 1.1, -1)

                MarketPrice.objects.create(
                    market=market,
                    commodity=commodity,
                    price_ugx=price,
                    price_min=price_min,
                    price_max=price_max,
                    recorded_at=now - timedelta(hours=random.randint(0, 48)),
                    recorded_by='Kilimo Hub Agent',
                )
                prices_created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {prices_created} price entries'))
        self.stdout.write(f'Totals: {Market.objects.count()} markets, {Commodity.objects.count()} commodities, {MarketPrice.objects.count()} prices')
