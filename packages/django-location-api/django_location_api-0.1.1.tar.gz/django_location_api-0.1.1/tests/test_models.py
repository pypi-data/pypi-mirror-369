from django.contrib.gis.geos import Point
from django.test import TestCase

from location_api.models import Location
from tests.factories import LocationFactory


class LocationTest(TestCase):
    def test_location(self):
        location = Location.objects.create(
            point=Point(-38.144275, 176.282217),
            country_code="NZ",
            gisprecision="number",
        )
        location.__str__()

    def test_url(self):
        location = LocationFactory()
        url = location.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
