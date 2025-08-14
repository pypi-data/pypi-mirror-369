from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from location_api.models import Location


class LocationSerializer(
    serializers.HyperlinkedModelSerializer, GeoFeatureModelSerializer
):
    supplier = serializers.StringRelatedField()

    class Meta:
        model = Location
        geo_field = "point"
        fields = (
            "id",
            "country_code",
            "gisprecision",
            "url",
            "name",
            "supplier",
            "attributes",
        )
