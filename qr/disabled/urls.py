from django.conf.urls import url, include
from rest_framework_nested import routers

from disabled import views

from core import views as coreviews


router = routers.DefaultRouter()
router.register(r'companies', coreviews.auxViewSet)
router.register(r'disabled-companies', views.DisableModelsViewSet)
disabled_models_router = routers.NestedSimpleRouter(router,
                                         r'companies',
                                         lookup='company')
disabled_models_router.register(r'disabled-models', views.DisableModelsViewSet, base_name='disabled-models')

urlpatterns = [
    #url(r'^', include(disabled_models_router.urls)),
    url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/disabled-models/$',
        views.DisableModelsViewSet.as_view(), name='lost_item')
]
