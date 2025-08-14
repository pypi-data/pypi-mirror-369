from django.contrib.gis.geos import Polygon
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_gis.filters import InBBoxFilter
from rest_framework.renderers import JSONRenderer

from location_api.models import Location
from location_api.serializers import LocationSerializer


class InBBoxFilterGoogle(InBBoxFilter):
    bbox_param = "in_gbbox"  # The URL query parameter which contains the bbox.

    def get_filter_bbox(self, request):
        bbox_string = request.query_params.get(self.bbox_param, None)
        if not bbox_string:
            return None

        try:
            lat_lo, lng_lo, lat_hi, lng_hi = (float(n) for n in bbox_string.split(","))
        except ValueError:
            raise ParseError(
                f"Invalid bbox string supplied for parameter {self.bbox_param}"
            )

        # min Lon, min Lat, max Lon, max Lat
        x = Polygon.from_bbox((lng_lo, lat_lo, lng_hi, lat_hi))
        return x

    def filter_queryset(self, request, queryset, view):
        queryset = super().filter_queryset(request, queryset, view)

        return queryset


class LocationViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows locations to be viewed or edited.

        /api/location/1

        {
            "id": 1,
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    175.4909113113731,
                    -37.775447241640535
                ]
            },
            "properties": {
                "country_code": "NZ",
                "gisprecision": "",
                "url": "http://127.0.0.1:8000/api/location/1?format=api",
                "name": "Cambridge",
                "supplier": "CCS",
                "attributes": {
                    "chargers": [
                        {
                            "type": "CCS",
                            "power": "50kW",
                            "price": "0.80"
                        }
                    ]
                }
            }
        }

        /api/location/?in_bbox=-90,29,-89,35
        min Lon, min Lat, max Lon, max Lat

        lat_lo,lng_lo,lat_hi,lng_hi

        {"type":"FeatureCollection","features":[{"id":24,"type":"Feature","geometry":{"type":"Point","coordinates":[175.28016,-37.791108]},"properties":{"location_id":23,"country_code":"NZ","gisprecision":"manual"}}]}
    """

    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    bbox_filter_field = "point"
    filter_backends = (InBBoxFilter, InBBoxFilterGoogle)


class LocationSearchView(APIView):
    """
    API endpoint that allows locations to be searched.

    [{"value": "location_id-location_slug", "label": "location_name"}]
    """

    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        if "term" in request.GET:
            terms = [x for x in request.GET["term"].split(" ") if x]

            # Build a combined Q object that requires ALL terms to match
            query = Q()

            # TODO this search needs to cover attributes JSONField too
            for term in terms:
                term_query = (
                    Q(name__icontains=term)
                    | Q(supplier__name__icontains=term)
                )
                query &= term_query

            locations = Location.objects.filter(query).order_by("name")

            location_data = [
                    {
                        "label": "%s" % location,
                        "value": f"{location.id}-{location.slug}",
                    }
                    for location in locations
                ]

            return Response(location_data)
        else:
            return Response(
                {"detail": "No search term provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
