from django.conf.urls import url, include
from rest_framework_nested import routers
from core import views

router = routers.DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
seat_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
seat_router.register(r'seats', views.SeatViewSet, base_name='company-seats')
user_router = routers.NestedSimpleRouter(seat_router,
                                         r'seats',
                                         lookup='seat')
user_router.register(r'users', views.SeatUserViewSet, base_name='seat-user')
visitor_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
visitor_router.register(r'visitors', views.CompanyVisitor, base_name='company-visitor')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(seat_router.urls)),
    url(r'^', include(user_router.urls)),
    url(r'^', include(visitor_router.urls)),
    url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/address/$', views.SeatAddress.as_view(), name='SeatAddress'),
    url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/users/(?P<user_pk>\d+)/custom/$', views.SeatCustomUserDetail.as_view(), name='SeatUserList'),
]
