from django.urls import include, path

urlpatterns = [
    path("api/", include("location_api.urls")),
    path("", include("location_api.urls.search")),
]
