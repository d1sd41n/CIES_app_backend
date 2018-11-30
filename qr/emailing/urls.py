from django.conf.urls import include, url
from rest_framework_nested import routers

from . import views

urlpatterns = [
    url(r'^companies/(?P<company_pk>\d+)/seats/(?P<seat_pk>\d+)/email/$',
        views.EmailLostItem.as_view(), name='lost_item')
]
