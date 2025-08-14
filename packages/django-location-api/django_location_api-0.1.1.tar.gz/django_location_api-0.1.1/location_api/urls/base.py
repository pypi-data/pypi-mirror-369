from rest_framework import routers

from location_api.views import LocationViewSet


router = routers.DefaultRouter()
router.register(r"location", LocationViewSet)

urlpatterns = router.urls
