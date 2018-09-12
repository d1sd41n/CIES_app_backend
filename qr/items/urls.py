from django.conf.urls import include, url
from rest_framework_nested import routers

from core import views as coreviews
from items import views

router = routers.DefaultRouter()
router.register(r'companies', coreviews.auxViewSet)
type_Item_router = routers.NestedSimpleRouter(router,
                                              r'companies',
                                              lookup='company')
type_Item_router.register(
    r'typeitem', views.CompanyTypeItem, base_name='company-type_item')
brand_router = routers.NestedSimpleRouter(type_Item_router,
                                          r'typeitem',
                                          lookup='typeitem')
brand_router.register(r'brand', views.BrandItem, base_name='brand_item')
seat_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
seat_router.register(r'seats', coreviews.auxViewSet, base_name='company-seats')
item_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
item_router.register(r'items', views.ItemViewSet, base_name='company-items')
Seat_Check_router = routers.NestedSimpleRouter(seat_router,
                                               r'seats',
                                               lookup='seat')
Seat_Check_router.register(
    r'check', views.CheckInViewSet, base_name='check-seat')


urlpatterns = [
    url(r'^', include(type_Item_router.urls)),
    url(r'^', include(item_router.urls)),
    url(r'^', include(brand_router.urls)),
    url(r'^', include(Seat_Check_router.urls)),
    url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/registeritem/$',
        views.RegisterItemViewSet.as_view(), name='register_item'),
    url(r'^companies/(?P<company_pk>\d+)/lostitem/$',
        views.LostItemView.as_view(), name='lost_item')
]
