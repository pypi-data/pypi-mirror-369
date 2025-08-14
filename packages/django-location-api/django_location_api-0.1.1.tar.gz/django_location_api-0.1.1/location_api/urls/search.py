from django.urls import path

from location_api.views import LocationSearchView

urlpatterns = [
    path("search/", LocationSearchView.as_view(), name="search"),
]
