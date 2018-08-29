from django.conf.urls import include, url
from rest_framework_nested import routers

from codes import views
from core import views as coreviews

router = routers.DefaultRouter()
router.register(r'companies', coreviews.auxViewSet)
company_codes_router = routers.NestedSimpleRouter(router,
                                                  r'companies',
                                                  lookup='company')
company_codes_router.register(r'companycodes', views.CompanyCodes,
                              base_name='company-codes')
seat_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
seat_router.register(r'seats', coreviews.auxViewSet, base_name='company-seats')
# generate_codes_router = routers.NestedSimpleRouter(router,
#                                                    r'companies',
#                                                    lookup='company')
# generate_codes_router.register(r'generate_codes', views.GenerateCodes,
#                                base_name='generate-codes')
urlpatterns = [
    url(r'^', include(company_codes_router.urls)),
    # url(r'^', include(generate_codes_router.urls)),
    url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/generate_codes/',
        views.GenerateCodes.as_view(), name="pdf"),
]
