from django.core.management.base import BaseCommand
from core.models import Alert


# Disease alerts mapped to specific districts based on real Ugandan agricultural patterns
DISTRICT_ALERTS = [
    # Central Uganda
    {"title": "Fall Armyworm outbreak in Maize", "body": "High Fall Armyworm activity reported in Central Uganda. Scout maize whorls for larvae and frass. Treat with Emamectin benzoate (0.5g/L) at dusk.", "severity": "danger", "district": "mukono"},
    {"title": "Coffee Wilt Disease confirmed", "body": "Coffee Wilt Disease (Fusarium xylarioides) detected in Robusta coffee farms in Mukono. Uproot and burn infected trees. Report to UCDA.", "severity": "danger", "district": "mukono"},
    {"title": "Fall Armyworm activity elevated", "body": "Fall Armyworm detected in multiple maize fields in Kampala periphery. Inspect whorls for caterpillars and frass. Apply Emamectin benzoate.", "severity": "warning", "district": "kampala"},
    {"title": "Banana Xanthomonas Wilt alert", "body": "Banana Xanthomonas Wilt spreading in Wakiso banana farms. Remove entire infected mats including rhizome. Disinfect tools with JIK.", "severity": "danger", "district": "wakiso"},
    {"title": "Bean Anthracnose risk", "body": "Wet conditions favoring Bean Anthracnose in Wakiso. Use certified seed and apply copper-based fungicide at first signs.", "severity": "warning", "district": "wakiso"},
    {"title": "Tomato Late Blight warning", "body": "Late Blight (Phytophthora infestans) reported in Masaka tomato farms. Apply Metalaxyl + Mancozeb. Remove affected leaves immediately.", "severity": "warning", "district": "masaka"},

    # Eastern Uganda
    {"title": "Cassava Mosaic Disease spread", "body": "Cassava Mosaic Disease spreading in Jinja. Remove infected plants and control whitefly vectors. Plant resistant varieties.", "severity": "danger", "district": "jinja"},
    {"title": "Fall Armyworm in Eastern maize", "body": "Fall Armyworm detected across Jinja and Mbale maize fields. Spray Emamectin benzoate into whorl. Use Push-Pull technology.", "severity": "warning", "district": "mbale"},
    {"title": "Bean Root Rot after rains", "body": "Bean Root Rot (Fusarium solani) appearing in Soroti after heavy rains. Improve drainage and use Carboxin + Thiram seed treatment.", "severity": "warning", "district": "soroti"},
    {"title": "Cassava Brown Streak Disease", "body": "Cassava Brown Streak Disease confirmed in Tororo. Remove and burn infected plants. Use resistant varieties for next planting.", "severity": "danger", "district": "tororo"},

    # Northern Uganda
    {"title": "Fall Armyworm in Northern maize", "body": "Fall Armyworm activity increasing in Gulu and Lira maize farms. Scout fields weekly. Treat early with Emamectin benzoate or Spinosad.", "severity": "warning", "district": "gulu"},
    {"title": "Groundnut Rust risk", "body": "Humid conditions favoring Groundnut Rust in Lira. Apply Propiconazole at first sign of orange pustules on leaves.", "severity": "info", "district": "lira"},
    {"title": "Sorghum Midge alert", "body": "Sorghum Midge causing grain sterility in Arua. Spray Dimethoate during flowering period for 2-3 weeks.", "severity": "warning", "district": "arua"},

    # Western Uganda
    {"title": "Coffee Berry Disease risk", "body": "Coffee Berry Disease (Colletotrichum kahawae) risk high in Mbarara coffee farms. Apply Copper Hydroxide before and during flowering.", "severity": "warning", "district": "mbarara"},
    {"title": "Banana Black Sigatoka", "body": "Black Sigatoka detected in Fort Portal banana plantations. Remove and destroy infected leaves. Apply Copper + Mancozeb fungicide.", "severity": "danger", "district": "fort portal"},
    {"title": "Late Blight in Irish Potatoes", "body": "Late Blight (Phytophthora infestans) threatening Irish Potato crops in Kabale. Apply Metalaxyl + Mancozeb. Ensure good drainage.", "severity": "danger", "district": "kabale"},
    {"title": "Maize Gray Leaf Spot", "body": "Grey Leaf Spot appearing in Hoima maize fields after prolonged wet weather. Apply Mancozeb (2.5g/L). Use resistant varieties next season.", "severity": "warning", "district": "hoima"},

    # Nationwide alerts
    {"title": "Fall Armyworm nationwide advisory", "body": "Fall Armyworm remains active across Uganda during this season. All maize farmers should scout fields weekly and treat early. Use Push-Pull for long-term control.", "severity": "info", "district": ""},
    {"title": "MAAIF livestock vaccination drive", "body": "Ministry of Agriculture conducting FMD and Rift Valley Fever vaccination in selected districts. Contact your district veterinary officer for schedules.", "severity": "info", "district": ""},
]


class Command(BaseCommand):
    help = 'Seed disease alerts for specific districts'

    def handle(self, *args, **options):
        created = 0
        for alert_data in DISTRICT_ALERTS:
            obj, was_created = Alert.objects.get_or_create(
                title=alert_data['title'],
                defaults={
                    'body': alert_data['body'],
                    'severity': alert_data['severity'],
                    'category': 'disease',
                    'district': alert_data['district'],
                    'source': 'Kilimo Hub',
                    'is_active': True,
                }
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} disease alerts (total: {Alert.objects.filter(category="disease").count()})'
        ))
