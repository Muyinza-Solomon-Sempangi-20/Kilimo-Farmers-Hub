from django.core.management.base import BaseCommand
from weather.models import WeatherCache


class Command(BaseCommand):
    help = 'Clear all weather cache entries'

    def handle(self, *args, **options):
        count = WeatherCache.objects.count()
        WeatherCache.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} cached weather entries'))
