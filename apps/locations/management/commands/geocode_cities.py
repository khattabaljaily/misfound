import json
import time
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand

from apps.locations.models import City

NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
USER_AGENT = 'Misfound/1.0 (lost-and-found platform; contact: khattabaljaily@gmail.com)'
REQUEST_DELAY_SECONDS = 1.1

# Loose bounding box covering every country this platform serves (Mauritania to
# Iraq/Oman, Comoros to Syria). Nominatim occasionally mismatches an ambiguous or
# contested place name to somewhere on a different continent entirely (e.g. it once
# resolved "Jerusalem" to a town in Alabama, USA) — results outside this box are
# rejected as a mismatch rather than saved.
ARAB_WORLD_BOUNDS = {'lat': (-13, 38), 'lng': (-18, 60)}


class Command(BaseCommand):
    help = 'Geocodes cities missing lat/lng via OpenStreetMap Nominatim, for the Browse map view.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all', action='store_true',
            help='Re-geocode every city, including ones that already have coordinates.'
        )

    def handle(self, *args, **options):
        cities = City.objects.select_related('country').all()
        if not options['all']:
            cities = cities.filter(lat__isnull=True)

        total = cities.count()
        if not total:
            self.stdout.write(self.style.SUCCESS('Nothing to geocode.'))
            return

        found, missed = 0, 0
        for i, city in enumerate(cities, start=1):
            query = f'{city.name_en}, {city.country.name_en}'
            coords = self._geocode(query)
            if coords:
                city.lat, city.lng = coords
                city.save(update_fields=['lat', 'lng'])
                found += 1
                self.stdout.write(f'[{i}/{total}] {query} -> {coords}')
            else:
                missed += 1
                self.stdout.write(self.style.WARNING(f'[{i}/{total}] {query} -> not found'))
            time.sleep(REQUEST_DELAY_SECONDS)

        self.stdout.write(self.style.SUCCESS(f'Done. Geocoded {found}, missed {missed}.'))

    def _geocode(self, query):
        params = urllib.parse.urlencode({'q': query, 'format': 'json', 'limit': 1})
        req = urllib.request.Request(f'{NOMINATIM_URL}?{params}', headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                results = json.loads(resp.read())
            if results:
                lat, lng = float(results[0]['lat']), float(results[0]['lon'])
                lat_min, lat_max = ARAB_WORLD_BOUNDS['lat']
                lng_min, lng_max = ARAB_WORLD_BOUNDS['lng']
                if not (lat_min <= lat <= lat_max and lng_min <= lng <= lng_max):
                    self.stderr.write(self.style.ERROR(
                        f'  rejected "{query}": result ({lat}, {lng}) is outside the expected region'
                    ))
                    return None
                return lat, lng
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'  error geocoding "{query}": {e}'))
        return None
