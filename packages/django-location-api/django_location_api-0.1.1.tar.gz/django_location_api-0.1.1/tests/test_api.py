from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories import (LocationFactory, SupplierFactory)


class LocationTests(APITestCase):
    def setUp(self):
        supplier = SupplierFactory()
        self.location = LocationFactory(supplier=supplier)

    def test_location_detail(self):
        """
        Ensure we can get a location.
        """
        url = reverse("location-detail", kwargs={"pk": self.location.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_list(self):
        url = reverse("location-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["features"], [])

    def test_location_bbox_search(self):
        url = reverse("location-list") + "?in_gbbox=-37.802284,175.213435,-37.765111,175.351365"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["features"], [])
        for feature in response.data["features"]:
            self.assertEqual(feature["id"], self.location.id)

    def test_search_get(self):
        url = reverse("search") + f"?term={self.location.name}"
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp.data,
            [
                {
                    "value": f"{self.location.id}-{self.location.slug}",
                    "label": self.location.name,
                }
            ],
        )

    def test_search_post(self):
        url = reverse("search")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 405)

    def test_search_bad_request(self):
        url = reverse("search")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 400)
