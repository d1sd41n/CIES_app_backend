from django.conf.urls import url, include
from rest_framework_nested import routers
from ubication.views import (CountryViewSet,
                             ProvinceViewSet,
                             CityViewSet)


router = routers.DefaultRouter()
router.register(r'countries', CountryViewSet)

province_router = routers.NestedSimpleRouter(router,
                                             r'countries',
                                             lookup='country')
province_router.register(r'provinces', ProvinceViewSet, base_name='country-provinces')

city_router = routers.NestedSimpleRouter(province_router,
                                         r'provinces',
                                         lookup='province')
city_router.register(r'cities', CityViewSet, base_name='province-cities')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(province_router.urls)),
    url(r'^', include(city_router.urls)),
]
