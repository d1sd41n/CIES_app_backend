from django.conf.urls import url, include
from rest_framework_nested import routers
from ubication.views import (CountryViewSet,
                             RegionViewSet,
                             CityViewSet)


router = routers.DefaultRouter()
router.register(r'countries', CountryViewSet)

region_router = routers.NestedSimpleRouter(router,
                                           r'countries',
                                           lookup='country')
region_router.register(r'regions', RegionViewSet, base_name='country-regions')

city_router = routers.NestedSimpleRouter(region_router,
                                         r'regions',
                                         lookup='region')
city_router.register(r'cities', CityViewSet, base_name='region-cities')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(region_router.urls)),
    url(r'^', include(city_router.urls)),
]
