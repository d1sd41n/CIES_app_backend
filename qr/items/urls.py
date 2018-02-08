from django.conf.urls import url, include
from rest_framework_nested import routers
from items import views
from core import views as coreviews


router = routers.DefaultRouter()
router.register(r'companies', coreviews.CompanyViewSet)
seat_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
seat_router.register(r'seats', coreviews.SeatViewSet, base_name='company-seats')
Seat_Items_router = routers.NestedSimpleRouter(seat_router,
                                         r'seats',
                                         lookup='seat')
Seat_Items_router.register(r'items', views.RegisterItemViewSet, base_name='Items-seat')
item_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
item_router.register(r'items', views.ItemViewSet, base_name='company-items')
Seat_Check_router = routers.NestedSimpleRouter(seat_router,
                                         r'seats',
                                         lookup='seat')
Seat_Check_router.register(r'check', views.CheckInViewSet, base_name='check-seat')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(seat_router.urls)),
    url(r'^', include(Seat_Items_router.urls)),
    url(r'^', include(item_router.urls)),
    url(r'^', include(Seat_Check_router.urls)),
    # url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/address/$', views.SeatAddress.as_view(), name='SeatAddress'),
    # url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/users/(?P<user_pk>\d+)/custom/$', views.SeatCustomUserDetail.as_view(), name='SeatUserList'),
]
